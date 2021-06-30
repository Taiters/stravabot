#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from infx.stravabot_stack import StravabotStack


app = cdk.App()
StravabotStack(app, "StravabotStack")

app.synth()
