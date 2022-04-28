from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.core import Stack, DockerImage
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack

from b_cfn_lambda_layer.lambda_layer import LambdaLayer
from b_cfn_lambda_layer_test.integration.infrastructure.layer1 import root as root1
from b_cfn_lambda_layer_test.integration.infrastructure.layer2 import root as root2
from b_cfn_lambda_layer_test.integration.infrastructure.layer3 import root as root3


class Function3(Function):
    """
    Function that allows us to test whether multiple same layers override each other.
    """
    def __init__(self, scope: Stack):
        super().__init__(
            scope=scope,
            id=f'{TestingStack.global_prefix()}TestingFunction3',
            code=Code.from_inline(
                # Ensure that dummy module is accessible from lambda layer
                # and the parent directory is included.
                'from layer1.dummy_module import DummyModule as M1\n'
                'from layer2.dummy_module import DummyModule as M2\n'
                'from layer3.dummy_module import DummyModule as M3\n'
                '\n\n'
                'def handler(*args, **kwargs):\n'
                '    return dict(\n'
                # Use the dummy module to ensure everything works.
                '        Dummy1=M1.action(),\n'
                '        Dummy2=M2.action(),\n'
                '        Dummy3=M3.action()\n'
                '    )'
                '\n'
            ),
            handler='index.handler',
            runtime=Runtime.PYTHON_3_6,
            layers=[
                LambdaLayer(
                    scope=scope,
                    name=f'{TestingStack.global_prefix()}TestingLayer3_1',
                    source_path=root1,
                    code_runtimes=[Runtime.PYTHON_3_6, Runtime.PYTHON_3_7, Runtime.PYTHON_3_8],
                    docker_image='python:3.8'
                ),
                LambdaLayer(
                    scope=scope,
                    name=f'{TestingStack.global_prefix()}TestingLayer3_2',
                    source_path=root2,
                    code_runtimes=[Runtime.PYTHON_3_6, Runtime.PYTHON_3_7, Runtime.PYTHON_3_8],
                    # Test backwards compatibility.
                    docker_image=DockerImage('python:3.8')
                ),

                # Repeat same layer twice.
                LambdaLayer(
                    scope=scope,
                    name=f'{TestingStack.global_prefix()}TestingLayer3_3_1',
                    source_path=root3,
                    code_runtimes=[Runtime.PYTHON_3_6, Runtime.PYTHON_3_7, Runtime.PYTHON_3_8],
                ),
                LambdaLayer(
                    scope=scope,
                    name=f'{TestingStack.global_prefix()}TestingLayer3_3_2',
                    source_path=root3,
                    code_runtimes=[Runtime.PYTHON_3_6, Runtime.PYTHON_3_7, Runtime.PYTHON_3_8],
                )
            ]
        )
