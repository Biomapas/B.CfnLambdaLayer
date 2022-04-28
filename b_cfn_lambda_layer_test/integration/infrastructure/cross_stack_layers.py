from aws_cdk.aws_lambda import Runtime, Function, Code
from aws_cdk.core import Construct, Stack
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack

from b_cfn_lambda_layer.lambda_layer import LambdaLayer
from b_cfn_lambda_layer_test.integration.infrastructure.layer_cross_stack import root


class CrossStackLayers(Stack):
    def __init__(self, scope: Construct):
        super().__init__(scope=scope)

        stack_a = Stack(
            scope=self,
            id='StackA'
        )

        stack_b = Stack(
            scope=self,
            id='StackB'
        )

        # Create a layer in stack A, reference in function in stack B.
        layer_in_stack_a = LambdaLayer(
            scope=stack_a,
            name=f'{TestingStack.global_prefix()}Layer1',
            source_path=root,
            code_runtimes=[Runtime.PYTHON_3_6],
        )

        self.function = Function(
            scope=stack_b,
            id='FunctionInStackB',
            handler='index.handler',
            runtime=Runtime.PYTHON_3_6,
            code=Code.from_inline(
                'from layer_cross_stack.dummy_module import DummyModule\n'
                'def handler(*args, **kwargs):\n'
                '    return dict(\n'
                '        Dummy=DummyModule.action()\n'
                '    )'
                '\n'
            )
        )

        # Safe way to add layers to functions in different stacks.
        layer_in_stack_a.add_to_function(self.function)
