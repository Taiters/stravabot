from aws_xray_sdk.core import patch_all

from stravabot.bootstrap import bootstrap

patch_all()
api = bootstrap()


def handler(event, context):
    return api.handle(event, context)
