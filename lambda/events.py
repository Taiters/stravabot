import boto3
from aws_xray_sdk.core import patch_all

from stravabot.config import KV_STORE_TABLE
from stravabot.core.events import StravaEventHandler
from stravabot.db import KeyValueStore
from stravabot.models import StravaEvent
from stravabot.services.user import UserService

patch_all()
dynamodb = boto3.resource("dynamodb")
store = KeyValueStore(dynamodb.Table(KV_STORE_TABLE))
users = UserService(store)
strava_event_handler = StravaEventHandler(users)


def handler(event, context):
    strava_event_handler.handle(StravaEvent.from_dict(event))
