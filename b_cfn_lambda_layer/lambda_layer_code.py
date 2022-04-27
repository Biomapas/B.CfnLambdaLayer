import os
import shutil
from typing import Optional, List

from aws_cdk.aws_lambda import Code

from b_cfn_lambda_layer import root
from b_cfn_lambda_layer.dependency import Dependency
from b_cfn_lambda_layer.pip_install import PipInstall
from b_cfn_lambda_layer.tmp import docker_build_root


class LambdaLayerCode:
    DEFAULT_DOCKER_IMAGE = 'python:3.9'

    def __init__(
            self,
            source_path: str,
            additional_pip_install_args: Optional[str] = None,
            dependencies: Optional[List[Dependency]] = None,
            docker_image: Optional[str] = None
    ) -> None:
        """
        Constructor.

        :param source_path: Path to source-code to be bundled.
        :param additional_pip_install_args:
        :param dependencies:
        :param docker_image:
        """
        self.additional_pip_install_args = additional_pip_install_args
        self.dependencies = dependencies
        self.source_path = source_path
        self.source_path_dir_name = os.path.basename(self.source_path)
        self.docker_image = docker_image or self.DEFAULT_DOCKER_IMAGE

        # General docker outputs path.
        # According to documentation, all of the python code and python dependencies shall live in "python" dir:
        # https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html
        self.outputs_path = '/asset/python'

    def build(self) -> Code:
        # Before building, ensure source code is available for Dockerfile.
        self.__fresh_source_copy()

        # Now, after the source code was made available. Build the code with Docker.
        return Code.from_docker_build(
            path=root,
            build_args={
                # Custom docker image.
                'DOCKER_IMAGE': self.docker_image,

                # OS-level paths.
                'INPUTS_PATH': f'./tmp/{self.source_path_dir_name}',

                # Docker container-level paths.
                'OUTPUTS_PATH': self.outputs_path,

                # Prebuilt commands to install.
                'PIP_INSTALL': self.__dependencies_install_command(),
            },
        )

    def __dependencies_install_command(self) -> str:
        return PipInstall(
            dependencies=self.dependencies,
            additional_pip_install_args=self.additional_pip_install_args,
            output_directory=self.outputs_path
        ).build_command()

    def __fresh_source_copy(self) -> None:
        """
        Copies given lambda layer's source code to a directory where the Dockerfile is.
        This way a Dockerfile can access source code and build it.

        :return: No return.
        """
        # Give a unique directory for every source.
        docker_layer_build_dir = f'{docker_build_root}/{self.source_path_dir_name}'

        # Delete previous copied source.
        shutil.rmtree(docker_layer_build_dir, ignore_errors=True)

        # Copy a fresh source.
        shutil.copytree(
            src=self.source_path,
            # Duplicate parent dir so the source code could be imported as
            # "from parent.module import Module" instead of
            # "from module import Module".
            dst=f'{docker_layer_build_dir}/{self.source_path_dir_name}',
            dirs_exist_ok=True
        )
