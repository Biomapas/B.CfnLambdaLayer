from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.core import Stack
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack

from b_cfn_lambda_layer.lambda_layer import LambdaLayer
from b_cfn_lambda_layer.package_version import PackageVersion
from b_cfn_lambda_layer_test.integration.infrastructure.layer_source import root


class Function2(Function):
    def __init__(self, scope: Stack):
        super().__init__(
            scope=scope,
            id=f'{TestingStack.global_prefix()}TestingFunction2',
            code=Code.from_inline(
                'import urllib3\n'
                'from jose import jwk, jwt\n'
                'from jose.utils import base64url_decode\n'
                'import boto3\n'
                'import botocore\n'
                'from dummy_module import DummyModule\n'
                '\n\n'
                'def handler(*args, **kwargs):\n'
                '    return dict(\n'
                '        Boto3Version=boto3.__version__,\n'
                '        BotocoreVersion=botocore.__version__,\n'
                '        Dummy=DummyModule.action()\n'
                '    )'
                '\n'
            ),
            handler='index.handler',
            runtime=Runtime.PYTHON_3_6,
            layers=[
                LambdaLayer(
                    scope=scope,
                    name=f'{TestingStack.global_prefix()}TestingLayer2',
                    source_path=root,
                    code_runtimes=[Runtime.PYTHON_3_6, Runtime.PYTHON_3_7, Runtime.PYTHON_3_8],
                    dependencies={
                        'python-jose': PackageVersion.from_string_version('3.3.0'),
                        'boto3': PackageVersion.from_string_version('1.16.35'),
                        'botocore': PackageVersion.from_string_version('1.19.35')
                    }
                )
            ]
        )
