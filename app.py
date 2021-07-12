#!/usr/bin/env python3
from aws_cdk import core as cdk

from infx.certificate_stack import CertificateStack
from infx.stravabot_stack import StravabotStack

app = cdk.App()
CertificateStack(app, "StravaBotCertificateStack", env=cdk.Environment(region="us-east-1"))
StravabotStack(app, "StravabotStack")

app.synth()
