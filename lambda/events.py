import boto3
from aws_xray_sdk.core import patch_all

from stravabot.config import KV_STORE_TABLE
from stravabot.db import KeyValueStore
from stravabot.models import StravaEvent
from stravabot.processor import StravaEventProcessor
from stravabot.services.user import UserService

patch_all()
dynamodb = boto3.resource("dynamodb")
store = KeyValueStore(dynamodb.Table(KV_STORE_TABLE))
users = UserService(store)
event_processor = StravaEventProcessor(users)


def handler(event, context):
    event_processor.process(StravaEvent.from_dict(event))
