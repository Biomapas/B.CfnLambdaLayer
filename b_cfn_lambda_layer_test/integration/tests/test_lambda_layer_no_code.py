import json

from b_aws_testing_framework.credentials import Credentials
from botocore.response import StreamingBody

from b_cfn_lambda_layer_test.integration.infrastructure.main_stack import MainStack


def test_RESOURCE_lambda_layer_WITH_no_code_no_dependencies_EXPECT_execution_successful():
    """
    Test whether the layer provides necessary functionality.

    :return: No return.
    """
    # Create client for lambda service.
    lambda_client = Credentials().boto_session.client('lambda')

    # Invoke specific lambda function.
    response = lambda_client.invoke(
        FunctionName=MainStack.get_output(MainStack.LAMBDA_FUNCTION_5_NAME_KEY),
        InvocationType='RequestResponse'
    )

    # Parse the result.
    payload: StreamingBody = response['Payload']
    data = [item.decode() for item in payload.iter_lines()]
    data = json.loads(''.join(data))

    # Assert that the result is as expected.
    assert str(data.get('Key')) == '123', data
