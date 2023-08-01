# B.CfnLambdaLayer

![Pipeline](https://github.com/Biomapas/B.CfnLambdaLayer/workflows/Pipeline/badge.svg?branch=master)

Easy lambda dependency management is here!<br> This is an AWS CDK resource that acts as a
`LayerVersion` resource but with more convenient approach to specify and bundle dependencies.

### Description

AWS CDK already makes it incredibly simple to package code for lambda functions and 
layers by exposing `Code` resource and methods like `Code.from_asset()`. However, it is very
difficult to add additional dependencies to your layer code e.g. `jose`, `requests`, newer `boto3` library, etc.
This custom layer resource makes packaging code with dependencies extremely simple like 2 + 2! You 
simply specify a dictionary of dependencies to include and this resource will do the rest.
<br><br>
You should note that this resource uses `docker` to bundle code and dependencies.

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

#### Dependencies

The most convenient feature of this resource is easy dependency management. When creating a new layer
you simply supply a dictionary of dependencies, and they will be installed and packaged to you layer
at a deployment level:

```python
from b_cfn_lambda_layer.package_version import PackageVersion

dependencies = {
    'python-jose': PackageVersion.from_string_version('3.3.0'),
    'boto3': PackageVersion.from_string_version('1.16.35'),
    'botocore': PackageVersion.from_string_version('1.19.35')
}
```

#### Full example

This is a full example where we create a lambda layer and use it in lambda function.

```python
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk import Stack

from b_cfn_lambda_layer.lambda_layer import LambdaLayer
from b_cfn_lambda_layer.package_version import PackageVersion

# Create layer with custom dependencies.
layer = LambdaLayer(
    scope=Stack(...),
    name='TestLayer',
    # You can conveniently specify path to source code to include.
    # Or not specify it at all if you care only about dependencies.
    # source_path=None,
    source_path='/path/to/your/layer/source/code',
    code_runtimes=[Runtime.PYTHON_3_8, Runtime.PYTHON_3_9, Runtime.PYTHON_3_10],
    # You can conveniently specify dependencies to include.
    dependencies={
        'python-jose': PackageVersion.from_string_version('3.3.0'),
        'boto3': PackageVersion.from_string_version('1.16.35'),
        'botocore': PackageVersion.from_string_version('1.19.35')
    }
)

# Create a function with a layer.
Function(
    scope=Stack(...),
    id='MyFunction',
    code=Code.from_asset('/path/to/lambda/function/code'),
    handler='index.handler',
    runtime=Runtime.PYTHON_3_10,
    # Specify layers.
    layers=[layer]
)
```

#### Using layers in multiple stacks

We all know that we can not really share a lambda layer instance in multiple
stacks. If we do, the next update to the source code in the lambda layer would 
result in a failed deployment. 
This is because of cross-stack exports-imports. An example error  is given below:

> 2022-04-28 17:29:34 [    INFO] Stack | 2/4 | 5:29:31 PM | UPDATE_ROLLBACK_IN_P | AWS::CloudFormation::Stack | Stack Export Stack:Export cannot be updated as it is in use by StackB

Thankfully, this resource has solved the problem very conveniently. 

Firstly, create a layer in any stack you want:

```python
# Create the layer in any stack.
layer = LambdaLayer(
    scope=Stack(...),
    ...
)
```

Then add it to a lambda function:

```python
# Create a lambda function in any stack.
function = Function(
    scope=Stack(...),
    # DO NOT supply the layer directly as it will create a direct dependency
    # between the function and the layer. This is what causes the deployments
    # to fail if we update layer's source code.
    # layers=[layer]
    ...
)

# Instead, call "add_to_function" layer's method to enable that layer for the function.
# This method does not create a direct dependency effectively solving cross-stack problems.
layer.add_to_function(function)
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
