from aws_cdk import App

from b_cfn_lambda_layer_test.integration.infrastructure.main_stack import MainStack

app = App()
MainStack(app)
app.synth()
