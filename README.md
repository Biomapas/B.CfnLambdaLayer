# B.CfnLambdaLayer

An AWS CDK resource that adds additional functionality to `LayerVersion` lambda layer resource.

### Description

TODO

AWS CDK already makes it incredibly simple to package code for lambda functions and 
layers by exposing `Code` resource and methods like `Code.from_asset()`. This custom layer resource 
makes packaging code even more convenient. 

### Remarks

[Biomapas](https://www.biomapas.com/) aims to modernise life-science industry by sharing its IT knowledge with other companies and the community. 
This is an open source library intended to be used by anyone. 
Improvements and pull requests are welcome. 

### Related technology

- Python3
- Docker
- AWS CDK
- AWS CloudFormation
- AWS Lambda
- AWS Lambda Layer
- AWS Lambda Layer bundling with Docker

### Assumptions

This project assumes you know what Lambda functions are and how code is being shared between them
(Lambda layers). 

- Excellent knowledge in IaaC (Infrastructure as a Code) principles.
- Excellent knowledge in Lambda functions and Lambda layers.  
- Good experience in AWS CDK and AWS CloudFormation.
- Good Python skills and basis of OOP.

### Useful sources

- AWS CDK:<br>https://docs.aws.amazon.com/cdk/api/latest/docs/aws-construct-library.html
- AWS CloudFormation:<br>https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html
- Lambda layers:<br>https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html
- Lambda layers in AWS CDK:<br>https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_lambda/README.html

### Install

Before installing this library, ensure you have these tools setup:

- Python / Pip
- AWS CDK
- Docker

To install this project from source run:

```
pip install .
```


Or you can install it from a PyPi repository:

```
pip install b-cfn-lambda-layer
```


### Usage & Examples

```python
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.core import Stack

from b_cfn_lambda_layer.lambda_layer import LambdaLayer
from b_cfn_lambda_layer.package_version import PackageVersion

# Create a function with layer.
Function(
    scope=Stack(...),
    id='MyFunction',
    code=Code.from_asset('/path/to/lambda/function/code'),
    handler='index.handler',
    runtime=Runtime.PYTHON_3_6,
    # Specify layers.
    layers=[
        LambdaLayer(
            scope=Stack(...),
            name='TestLayer',
            source_path='/path/to/your/layer/source/code',
            code_runtimes=[Runtime.PYTHON_3_6, Runtime.PYTHON_3_7, Runtime.PYTHON_3_8],
            # You can conveniently specify dependencies to include.
            dependencies={
                'python-jose': PackageVersion.from_string_version('3.3.0'),
                'boto3': PackageVersion.from_string_version('1.16.35'),
                'botocore': PackageVersion.from_string_version('1.19.35')
            }
        )
    ]
)
```

### Testing

This package has integration tests based on **pytest**.
To run tests simply run:

```
pytest b_cfn_lambda_layer_test/integration/tests
```

### Contribution

Found a bug? Want to add or suggest a new feature? 
Contributions of any kind are gladly welcome. 
You may contact us directly, create a pull-request or an issue in github platform. 
Lets modernize the world together.
