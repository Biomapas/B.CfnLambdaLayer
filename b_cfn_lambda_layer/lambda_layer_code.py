import os
from os.path import exists
from typing import Optional, Dict

from aws_cdk.aws_lambda import Code

from b_cfn_lambda_layer import root
from b_cfn_lambda_layer.package_version import PackageVersion
from b_cfn_lambda_layer.pip_install import PipInstall


class LambdaLayerCode:
    DEFAULT_DOCKER_IMAGE = 'python:3.9'

    def __init__(
            self,
            source_path: str,
            include_parent: bool = True,
            additional_pip_install_args: Optional[str] = None,
            dependencies: Optional[Dict[str, PackageVersion]] = None,
            docker_image: Optional[str] = None
    ) -> None:
        """
        Constructor.

        :param source_path: Path to source-code to be bundled.
        :param include_parent: A flag to specify whether include source code parent directory.
            Read more:
            If it was specified to include "source path parent directory"
            when bundling source code, the final asset outputs python path will include
            that "source path parent directory". This means, that bundled module will be imported
            as "from parent_dir.a import A" instead of "from a import A".
        :param additional_pip_install_args:
        :param dependencies:
        :param docker_image:
        """
        self.additional_pip_install_args = additional_pip_install_args
        self.dependencies = dependencies
        self.source_path = source_path
        self.include_parent = include_parent
        self.docker_image = docker_image or self.DEFAULT_DOCKER_IMAGE
        self.source_path_parent = os.path.basename(self.source_path)

        """
        Docker outputs paths.
        """

        # General outputs path.
        # According to documentation, all of the python code and python dependencies shall live in "python" dir:
        # https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html
        self.outputs_path = '/asset/python'

        # Output directory for source code dependencies.
        self.dependencies_outputs_path = self.outputs_path

        # Output directory for source code.
        self.source_outputs_path = '/asset/python'
        if self.include_parent: self.source_outputs_path += f'/{self.source_path_parent}'

    def build(self) -> Code:
        return Code.from_docker_build(
            path=root,
            build_args={
                # Custom docker image.
                'DOCKER_IMAGE': self.docker_image,

                # OS-level paths.
                'INPUTS_PATH': self.source_path,

                # Docker container-level paths.
                'DOCKER_OUTPUTS_PATH': self.outputs_path,
                'DOCKER_DEPENDENCIES_OUTPUTS_PATH': self.dependencies_outputs_path,
                'DOCKER_SOURCE_OUTPUTS_PATH': self.source_outputs_path,

                # Prebuilt commands to install.
                'DEPENDENCIES_PIP_INSTALL': self.dependencies_install_command(),
                'REQUIREMENTS_PIP_INSTALL': self.requirements_install_command()
            },
        )

    def dependencies_install_command(self) -> str:
        return PipInstall(
            dependencies=self.dependencies,
            additional_pip_install_args=self.additional_pip_install_args,
            output_directory=self.dependencies_outputs_path
        ).build_command()

    def requirements_install_command(self) -> str:
        requirements_command = (
            f'pip install -r '
            f'{self.source_path}/requirements.txt '
            f'{self.additional_pip_install_args} -t '
            f'{self.dependencies_outputs_path}'
        )

        if exists(f'{self.source_path}/requirements.txt'):
            return requirements_command

        return requirements_command
