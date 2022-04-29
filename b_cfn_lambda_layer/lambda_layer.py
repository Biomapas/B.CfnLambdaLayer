import logging
from functools import lru_cache
from typing import List, Optional, Dict

from aws_cdk.aws_lambda import LayerVersion, Runtime, Function, ILayerVersion
from aws_cdk.aws_ssm import StringParameter
from aws_cdk.core import Stack, DockerImage

from b_cfn_lambda_layer.dependency import Dependency
from b_cfn_lambda_layer.lambda_layer_code import LambdaLayerCode
from b_cfn_lambda_layer.package_version import PackageVersion

LOGGER = logging.getLogger(__name__)


class LambdaLayer(LayerVersion):
    def __init__(
            self,
            scope: Stack,
            name: str,
            source_path: str,
            code_runtimes: List[Runtime],
            dependencies: Optional[Dict[str, PackageVersion]] = None,
            additional_pip_install_args: Optional[str] = None,
            docker_image: Optional[str] = None,
            # Better backwards compatibility.
            *args,
            **kwargs
    ) -> None:
        """
        Constructor.

        :param scope: Parent CloudFormation stack.
        :param name: Unique name of the layer.
        :param source_path: Path to source-code to be bundled.
        :param code_runtimes: Available runtimes for your code.
        :param dependencies: A dictionary of dependencies to include in the layer.
            Keys are dependency (package) names.
            Values are dependency (package) version objects.
        :param additional_pip_install_args: A string of additional pip-install arguments.
        :param docker_image: Docker image to use when building code.
        """
        self.__scope = scope
        self.__name = name

        # For better backwards compatibility.
        if isinstance(docker_image, DockerImage):
            docker_image = docker_image.image

        super().__init__(
            scope=self.__scope,
            id=self.__name,
            layer_version_name=self.__name,
            code=LambdaLayerCode(
                source_path=source_path,
                additional_pip_install_args=additional_pip_install_args,
                dependencies=[Dependency(key, value) for key, value in (dependencies or {}).items()],
                docker_image=docker_image
            ).build(),
            compatible_runtimes=code_runtimes
        )

        for argument in args:
            LOGGER.warning(f'Positional argument: ({argument}) is not supported!')

        for name, argument in kwargs.items():
            LOGGER.warning(f'Named argument: ({name}:{argument}) is not supported!')

        self.__ssm_arn = StringParameter(
            scope=scope,
            id=f'{self.__name}Arn',
            parameter_name=f'{self.__name}Arn',
            string_value=self.layer_version_arn
        )

    @lru_cache(maxsize=None)
    def copy(self, scope: Stack) -> ILayerVersion:
        """
        Creates a copy of a current layer that does not create a direct
        dependency between current layer instance and the resource that is using this layer.

        :param scope: A scope/stack in which this resource should be created. Note,
            that the scope should be the same as the resource's that is using the layer copy.
        :return: An indirect copy of this layer's instance.
        """
        return LayerVersion.from_layer_version_arn(
            scope=scope,
            id=f'{self.__name}Resolved',
            layer_version_arn=StringParameter.value_for_string_parameter(
                scope=scope,
                parameter_name=f'{self.__name}Arn'
            )
        )

    def add_to_function(self, *functions: Function) -> None:
        """
        Adds this layer to a given lambda function(s). Use this method if you
        want to use layers between multiple stacks and avoid breaking everything.

        Using this method does not create a direct dependency between the function and the layer.

        Read more why cross-stack dependencies between functions and layers are evil:
        https://gnomezgrave.com/2020/06/04/update-cross-stack-aws-lambda-layers/

        :param functions: Lambda function(s) to which this layer should be added.

        :return: No return.
        """
        for function in functions:
            # Add a dependency to the SSM parameter which has a dependency to the layer.
            # This creates an indirect dependency between the function and the layer.
            function.node.add_dependency(self.__ssm_arn)
            # Create the layer copy withing the same stack as the function.
            # I am not exactly sure why, but this makes everything to magically work.
            layer = self.copy(function.stack)
            function.add_layers(layer)
