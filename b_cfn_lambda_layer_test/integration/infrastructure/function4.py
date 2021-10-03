from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.core import Stack
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack

from b_cfn_lambda_layer.lambda_layer import LambdaLayer
from b_cfn_lambda_layer_test.integration.infrastructure.layer_source import root


class Function4(Function):
    """
    Function that allows us to test whether layer source code is included in the parent directory
    i.e. instead of "from a import A" you would get "from parent_dir.a import A".
    """
    def __init__(self, scope: Stack):
        super().__init__(
            scope=scope,
            id=f'{TestingStack.global_prefix()}TestingFunction4',
            code=Code.from_inline(
                # Ensure that dummy module is accessible from lambda layer
                # and the parent directory is included.
                'from layer_source.dummy_module import DummyModule\n'
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
                    name=f'{TestingStack.global_prefix()}TestingLayer4',
                    source_path=root,
                    code_runtimes=[Runtime.PYTHON_3_6, Runtime.PYTHON_3_7, Runtime.PYTHON_3_8],
                    include_source_path_directory=True
                )
            ]
        )
