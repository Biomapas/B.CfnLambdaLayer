import logging
from typing import List, Optional, Dict

from aws_cdk.aws_lambda import LayerVersion, Runtime
from aws_cdk.core import DockerImage
from aws_cdk.core import Stack

from b_cfn_lambda_layer.lambda_layer_code import LambdaLayerCode
from b_cfn_lambda_layer.package_version import PackageVersion

LOGGER = logging.getLogger(__name__)


class LambdaLayer(LayerVersion):
    def __init__(
            self,
            scope: Stack,
            layer_name: str,
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

        :param additional_pip_install_args: A string of additional pip-install arguments.
        :param dependencies: A dictionary of dependencies to include in the layer.
            Keys are dependency (package) names.
            Values are dependency (package) version objects.
        :param docker_image: Docker image to use when building code.
        """
        super().__init__(
            scope=scope,
            id=layer_name,
            layer_version_name=layer_name,
            code=LambdaLayerCode(
                source_path=source_path,
                include_parent=include_source_path_directory,
                additional_pip_install_args=additional_pip_install_args,
                dependencies=dependencies,
                docker_image=docker_image
            ).build(),
            compatible_runtimes=code_runtimes
        )
