import logging
import os
from typing import List, Optional, Dict

from aws_cdk.aws_lambda import Code
from aws_cdk.aws_lambda import LayerVersion, Runtime
from aws_cdk.core import BundlingOptions, AssetHashType, BundlingDockerImage, DockerImage
from aws_cdk.core import Stack

from b_cfn_lambda_layer.package_version import PackageVersion

LOGGER = logging.getLogger(__name__)


class LambdaLayer(LayerVersion):
    DOCKER_BUNDLING_TMP_OUTPUTS_DIR = '/tmp/lambda/outputs/'
    DOCKER_BUNDLING_ASSET_INPUTS = '/asset-input/'
    DOCKER_BUNDLING_ASSET_OUTPUTS = '/asset-output/'
    # According to documentation, all of the code and dependencies shall live in "python" dir:
    # https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html
    DOCKER_BUNDLING_ASSET_OUTPUTS_PYTHON = '/asset-output/python/'

    def __init__(
            self,
            scope: Stack,
            name: str,
            source_path: str,
            code_runtimes: List[Runtime],
            include_source_path_directory: bool = True,
            additional_pip_install_args: Optional[str] = None,
            dependencies: Optional[Dict[str, PackageVersion]] = None,
            docker_image: Optional[DockerImage] = None,
    ) -> None:
        """
        Constructor.

        :param scope: Parent CloudFormation stack.
        :param name: Unique name of the layer.
        :param source_path: Path to source-code to be bundled.
        :param code_runtimes: Available runtimes for your code.
        :param include_source_path_directory: When bundling source code - include source code's parent directory.
            E.g. if this setting is false, bundled module is imported like this: "from a import A". However,
            if this setting is true, bundled module is imported like this: "from parent_dir.a import A". Note,
            that other dependencies e.g. boto3, jwt, requests, or any other will remain importable as usual
            despite this setting e.g. "from boto3 import client".
        :param additional_pip_install_args: A string of additional pip-install arguments.
        :param dependencies: A dictionary of dependencies to include in the layer.
            Keys are dependency (package) names.
            Values are dependency (package) version objects.
        :param docker_image: Docker image to use when building code.
        """
        self.__scope = scope
        self.__name = name
        self.__source_path = source_path
        self.__runtimes = code_runtimes
        self.__include_source_path_directory = include_source_path_directory
        self.__additional_pip_install_args = additional_pip_install_args
        self.__dependencies = dependencies or {}
        self.__docker_image = docker_image

        self.__docker_bundling_tmp_outputs_dir = self.DOCKER_BUNDLING_TMP_OUTPUTS_DIR
        self.__docker_bundling_asset_inputs = self.DOCKER_BUNDLING_ASSET_INPUTS
        self.__docker_bundling_asset_outputs = self.DOCKER_BUNDLING_ASSET_OUTPUTS
        # Output directory for dependencies. Usually it should always be /asset-output/python/.
        self.__docker_bundling_asset_outputs_python_dependencies = self.DOCKER_BUNDLING_ASSET_OUTPUTS_PYTHON
        # Output directory for custom code. Usually it is /asset-output/python/ but if
        # "include_source_path_directory" setting is set to true then it will be something
        # like this - /asset-output/python/parent-dir/.
        self.__docker_bundling_asset_outputs_python_code = self.DOCKER_BUNDLING_ASSET_OUTPUTS_PYTHON

        # If it was specified to include "source path parent directory" when bundling source code,
        # modify the final asset outputs python path to include that "source path parent directory".
        # This means, that bundled module will be imported as "from parent_dir.a import A" instead of
        # "from a import A".
        if include_source_path_directory:
            source_directory_base_name = os.path.basename(self.__source_path)
            self.__docker_bundling_asset_outputs_python_code = (
                f'{self.__docker_bundling_asset_outputs_python_code}'
                f'{source_directory_base_name}/'
            )

        super().__init__(
            scope=scope,
            id=name,
            code=self.build(),
            compatible_runtimes=self.__runtimes
        )

    def build(self) -> Code:
        """
        Builds a code from source.

        :return: Built code that will be used for creating a Lambda layer.
        """
        command = (
                self.pre_install_command() +
                self.install_command(self.__additional_pip_install_args) +
                self.post_install_command() +
                self.pre_build_command() +
                self.build_command() +
                self.post_build_command()
        )

        # Just for logging and clarity purposes show the full trace of commands to be executed.
        command_log = '\n'.join(command)
        LOGGER.debug(f'Full bundling command:\n{command_log}.')

        code = Code.from_asset(
            path=self.__source_path,
            asset_hash_type=AssetHashType.BUNDLE,
            bundling=BundlingOptions(
                image=self.__docker_image or BundlingDockerImage.from_registry('python:3.9'),
                command=['bash', '-c', ' && '.join(command)]
            )
        )

        return code

    """
    Install commands.
    """

    def pre_install_command(self) -> List[str]:
        """
        Initial command to prepare environment for package and dependency installation.

        :return: List of pre-install commands.
        """
        return [
            # Assert that asset-input and asset-output directories are available.
            #
            # According to documentation: The AWS CDK mounts the folder specified as
            # the first argument to fromAsset at /asset-input inside the container,
            # and mounts the asset output directory (where the cloud assembly is staged)
            # at /asset-output inside the container.
            #
            # Read more documentation:
            # https://aws.amazon.com/blogs/devops/building-apps-with-aws-cdk/
            f'if [ ! -d {self.__docker_bundling_asset_inputs} ]; then echo "Directory {self.__docker_bundling_asset_inputs} not present!" && exit 1; fi',
            f'if [ ! -d {self.__docker_bundling_asset_outputs} ]; then echo "Directory {self.__docker_bundling_asset_outputs} not present!" && exit 1; fi',

            # Make temporary directory.
            f'mkdir -p {self.__docker_bundling_tmp_outputs_dir}',

            # List all insides of asset-input and tmp directories.
            f'echo "---------------------------- {self.__docker_bundling_asset_inputs} ----------------------------"',
            f'ls -la {self.__docker_bundling_asset_inputs}',
            f'echo "---------------------------- {self.__docker_bundling_tmp_outputs_dir} ----------------------------"',
            f'ls -la {self.__docker_bundling_tmp_outputs_dir}',
        ]

    def install_command(self, pip_install_args: Optional[str] = None) -> List[str]:
        pip_install_args = pip_install_args or self.__pip_upgrade_args()

        command = [
            # Try to find requirements file. If it exists run install.
            f'if [ -e {self.__docker_bundling_asset_inputs}requirements.txt ]; '
            f'then '
            f'pip install -r {self.__docker_bundling_asset_inputs}requirements.txt {pip_install_args} -t {self.__docker_bundling_tmp_outputs_dir}; '
            f'fi'
        ]

        # Create install commands for each dependency.
        for key, value in self.__dependencies.items():
            command.append(self.__create_install_dependency_command(
                dependency=key,
                dependency_version=value,
                install_args=pip_install_args
            ))

        return command

    def post_install_command(self) -> List[str]:
        return [
            # Just for debugging reasons list what's inside after installation.
            f'echo "---------------------------- {self.__docker_bundling_tmp_outputs_dir} ----------------------------"',
            f'ls -la {self.__docker_bundling_tmp_outputs_dir}'
        ]

    def pre_build_command(self) -> List[str]:
        return [
            # Make sure these output directories exist.
            f'mkdir -p {self.__docker_bundling_asset_outputs_python_code}',
            f'mkdir -p {self.__docker_bundling_asset_outputs_python_dependencies}',
        ]

    def build_command(self) -> List[str]:
        return [
            # Copy installed dependencies.
            f'cp -R {self.__docker_bundling_tmp_outputs_dir}. {self.__docker_bundling_asset_outputs_python_dependencies}.',

            # Copy source code.
            f'cp -R {self.__docker_bundling_asset_inputs}. {self.__docker_bundling_asset_outputs_python_code}.',
        ]

    def post_build_command(self) -> List[str]:
        return [
            # Cleanup.
            f'find  {self.__docker_bundling_asset_outputs} -type f -name "*.py[co]" -delete',
            f'find  {self.__docker_bundling_asset_outputs} -type d -name "__pycache__" -exec rm -rf {{}} +',
            f'find  {self.__docker_bundling_asset_outputs} -type d -name "*.dist-info" -exec rm -rf {{}} +',
            f'find  {self.__docker_bundling_asset_outputs} -type d -name "*.egg-info" -exec rm -rf {{}} +',

            # Clean tmp directory for reuse.
            f'rm -rf {self.__docker_bundling_tmp_outputs_dir}',

            # List asset-output contents.
            f'echo "---------------------------- {self.__docker_bundling_asset_outputs_python_code} ----------------------------"',
            f'ls -la {self.__docker_bundling_asset_outputs_python_code}.',
            f'echo "---------------------------- {self.__docker_bundling_asset_outputs_python_dependencies} ----------------------------"',
            f'ls -la {self.__docker_bundling_asset_outputs_python_dependencies}.',

            # Calculate asset-output hash.
            f'echo "---------------------------- {self.__docker_bundling_asset_outputs} hash ----------------------------"',
            f'find {self.__docker_bundling_asset_outputs} -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum',

            # Success!
            'echo "\n---------------- build successful ----------------\n"',
        ]

    """
    Helper methods.
    """

    def __create_install_dependency_command(
            self,
            dependency: str,
            dependency_version: Optional[PackageVersion] = None,
            install_args: Optional[str] = None
    ) -> str:
        """
        Creates a "pip install" command for specific dependency (package).

        :param dependency: Dependency name e.g. 'jwt'.
        :param dependency_version: Dependency version.
        :param install_args: Additional installation arguments for pip.

        :return: Install command as a string.
        """
        version = dependency_version or PackageVersion(version_type=PackageVersion.VersionType.LATEST)
        install_args = install_args or ''

        if version.version_type == PackageVersion.VersionType.LATEST:
            install_args += f' {LambdaLayer.__pip_upgrade_args()}'
            return (
                f'pip install {dependency} {install_args} '
                f'-t {self.__docker_bundling_tmp_outputs_dir}'
            )

        elif version.version_type == PackageVersion.VersionType.SPECIFIC:
            return (
                f'pip install {dependency}=={version.version_string} {install_args} '
                f'-t {self.__docker_bundling_tmp_outputs_dir}'
            )

        elif version.version_type == PackageVersion.VersionType.NONE:
            return ''

        raise ValueError('Unsupported enum value.')

    @staticmethod
    def __pip_upgrade_args() -> str:
        """
        Pip upgrade arguments that can be used next to "pip install xxx" command to enforce package upgrade.

        :return: Returns arguments as a string that ensure package upgrade.
        """
        return '--upgrade --upgrade-strategy eager'
