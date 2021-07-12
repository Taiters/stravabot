import boto3
from aws_xray_sdk.core import patch_all
from slack_bolt import App

from stravabot.config import CDN_BUCKET, KV_STORE_TABLE
from stravabot.db import KeyValueStore
from stravabot.models import StravaEvent
from stravabot.processor import StravaEventProcessor
from stravabot.services.map import MapService
from stravabot.services.slack import SlackService
from stravabot.services.strava import StravaService
from stravabot.services.user import UserService

patch_all()
app = App(process_before_response=True)
dynamodb = boto3.resource("dynamodb")
s3 = boto3.resource("s3")
store = KeyValueStore(dynamodb.Table(KV_STORE_TABLE))
users = UserService(store)
strava = StravaService(users)
maps = MapService(s3.Bucket(CDN_BUCKET))
slack = SlackService(app)

event_processor = StravaEventProcessor(users, strava, maps, slack)


def handler(event, context):
    event_processor.process(StravaEvent.from_dict(event))
