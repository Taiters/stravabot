from typing import Optional

from aws_cdk import core as cdk
from aws_cdk.aws_certificatemanager import Certificate, CertificateValidation

from infx.config import DOMAIN


class CertificateStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, env: Optional[cdk.Environment]) -> None:
        super().__init__(scope, construct_id, env=env)
        self.certificate = Certificate(
            self,
            "Certificate",
            domain_name=f"cdn.{DOMAIN}",
            validation=CertificateValidation.from_dns(),
        )
