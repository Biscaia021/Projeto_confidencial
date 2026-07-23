import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_app.cdk_app_stack import CdkAppStack

def test_infrastructure_created():
    app = core.App()
    stack = CdkAppStack(app, "cdk-app")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::EC2::VPC", 1)
    
    template.resource_count_is("AWS::S3::Bucket", 1)

    template.resource_count_is("AWS::CloudFront::Distribution", 1)

    template.resource_count_is("AWS::ApiGateway::RestApi", 1)

    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "index.handler"
    })
