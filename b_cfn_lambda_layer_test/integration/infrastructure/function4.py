from aws_cdk import Stack
from aws_cdk.aws_lambda import Function, Code, Runtime
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack

from b_cfn_lambda_layer.lambda_layer import LambdaLayer


class Function4(Function):
    """
    Function that allows us to test whether the layer can contain nothing.
    """

    def __init__(self, scope: Stack):
        super().__init__(
            scope=scope,
            id=f'{TestingStack.global_prefix()}TestingFunction4',
            code=Code.from_inline(
                'def handler(*args, **kwargs):\n'
                '    return dict(\n'
                '        Key=123\n'
                '    )'
                '\n'
            ),
            handler='index.handler',
            runtime=Runtime.PYTHON_3_10,
            layers=[
                LambdaLayer(
                    scope=scope,
                    name=f'{TestingStack.global_prefix()}TestingLayer4'
                )
            ]
        )
