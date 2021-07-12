from aws_cdk import core as cdk
from aws_cdk.custom_resources import (
    AwsCustomResource,
    AwsCustomResourcePolicy,
    AwsSdkCall,
    PhysicalResourceId,
)


class CdnCertificate(cdk.Construct):
    def __init__(self, scope: cdk.Construct, id: str):
        super().__init__(scope, id)

        resource = AwsCustomResource(
            self,
            "Certificate",
            on_create=AwsSdkCall(
                service="ACM",
                action="listCertificates",
                region="us-east-1",
                physical_resource_id=PhysicalResourceId.from_response("CertificateSummaryList.0.CertificateArn"),
            ),
            policy=AwsCustomResourcePolicy.from_sdk_calls(resources=AwsCustomResourcePolicy.ANY_RESOURCE),
        )

        self.certificate_arn = resource.get_response_field("CertificateSummaryList.0.CertificateArn")
