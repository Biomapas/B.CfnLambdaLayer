from aws_cdk.core import Construct
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack

from b_cfn_lambda_layer_test.integration.infrastructure.function1 import Function1
from b_cfn_lambda_layer_test.integration.infrastructure.function2 import Function2


class MainStack(TestingStack):
    LAMBDA_FUNCTION_1_NAME_KEY = 'LambdaFunction1Name'
    LAMBDA_FUNCTION_2_NAME_KEY = 'LambdaFunction2Name'

    def __init__(self, scope: Construct):
        super().__init__(scope=scope)

        self.function1 = Function1(self)
        self.function2 = Function2(self)

        self.add_output(self.LAMBDA_FUNCTION_1_NAME_KEY, value=self.function1.function_name)
        self.add_output(self.LAMBDA_FUNCTION_2_NAME_KEY, value=self.function2.function_name)
