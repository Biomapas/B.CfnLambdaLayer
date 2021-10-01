from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.core import Stack
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack

from b_cfn_lambda_layer.lambda_layer import LambdaLayer
from b_cfn_lambda_layer_test.integration.infrastructure.layer_source import root


class Function1(Function):
    def __init__(self, scope: Stack):
        super().__init__(
            scope=scope,
            id=f'{TestingStack.global_prefix()}TestingFunction1',
            code=Code.from_inline(
                # Ensure that dummy module is accessible from lambda layer.
                'from dummy_module import DummyModule\n'
                '\n\n'
                'def handler(*args, **kwargs):\n'
                '    return dict(\n'
                # Use the dummy module to ensure everything works.
                '        Dummy=DummyModule.action()\n'
                '    )'
                '\n'
            ),
            handler='index.handler',
            runtime=Runtime.PYTHON_3_6,
            layers=[
                LambdaLayer(
                    scope=scope,
                    name=f'{TestingStack.global_prefix()}TestingLayer1',
                    source_path=root,
                    code_runtimes=[Runtime.PYTHON_3_6, Runtime.PYTHON_3_7, Runtime.PYTHON_3_8]
                )
            ]
        )
