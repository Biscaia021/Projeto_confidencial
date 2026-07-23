from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_s3_deployment as s3deploy,
)
from constructs import Construct
import os

class CdkAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. 100% Free Tier VPC (nat_gateways=0 ensures zero NAT Gateway hourly charges!)
        vpc = ec2.Vpc(
            self,
            "AppVpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ]
        )

        # 2. S3 Bucket for Static Website Hosting (AWS Free Tier - 5GB Storage)
        website_bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # 3. CloudFront Distribution (AWS Free Tier - 1TB Transfer / 10M Requests)
        distribution = cloudfront.Distribution(
            self,
            "WebsiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3StaticWebsiteOrigin(website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            default_root_object="index.html",
        )

        # 4. Lambda Function using OpenRouter Free Gemma Model (AWS Free Tier - 1M Requests/mo)
        # Executing without VPC NAT Gateway allows direct HTTPS calls to openrouter.ai at $0 cost!
        api_handler = _lambda.Function(
            self,
            "ApiHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=_lambda.Code.from_asset("cdk_app/lambda_src"),
            environment={
                "OPENROUTER_MODEL": "google/gemma-2-9b-it:free",
                "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY", "")
            },
            timeout=Stack.of(self).format_string("{0}", 30) if False else None,
        )

        # 5. API Gateway REST API (AWS Free Tier - 1M Calls/mo)
        api = apigw.LambdaRestApi(
            self,
            "ApiGateway",
            handler=api_handler,
            proxy=True,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization", "X-Title"],
            ),
        )

        # 6. Deploy Frontend Assets to S3
        s3deploy.BucketDeployment(
            self,
            "DeployWebsite",
            sources=[s3deploy.Source.asset("./frontend")],
            destination_bucket=website_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        # CloudFormation Outputs
        CfnOutput(self, "WebsiteURL", value=f"https://{distribution.distribution_domain_name}")
        CfnOutput(self, "ApiGatewayURL", value=api.url)
        CfnOutput(self, "S3BucketName", value=website_bucket.bucket_name)


