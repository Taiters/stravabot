from contextlib import contextmanager

import boto3
from aws_xray_sdk.core import xray_recorder
from jinja2 import Environment, PackageLoader, select_autoescape
from slack_bolt import App

from stravabot.api import Api
from stravabot.config import JWT_SECRET_KEY, KV_STORE_TABLE, STRAVA_EVENT_HANDLER
from stravabot.config.base import AUTH_FLOW_TTL
from stravabot.db import KeyValueStore
from stravabot.handlers import StravaAuthHandler, StravaEventHandler
from stravabot.handlers.channel import ChannelHandler
from stravabot.services.event import EventService
from stravabot.services.response_url import ResponseUrlService
from stravabot.services.slack import SlackService
from stravabot.services.strava import StravaService
from stravabot.services.token import TokenService
from stravabot.services.user import UserService


@contextmanager
def traced(name):
    try:
        xray_recorder.begin_subsegment(name)
        yield
    finally:
        xray_recorder.end_subsegment()


@xray_recorder.capture("bootstrap")
def bootstrap() -> Api:
    with traced("init templates"):
        templates = Environment(
            loader=PackageLoader("stravabot"),
            autoescape=select_autoescape(),
        )

    with traced("init slack app"):
        app = App(process_before_response=True)

    with traced("init api"):
        api = Api(app)

    with traced("init dynamodb resource"):
        dynamodb = boto3.resource("dynamodb")

    with traced("init dynamodb table"):
        table = dynamodb.Table(KV_STORE_TABLE)

    with traced("init kv store"):
        store = KeyValueStore(table)

    with traced("init tokens"):
        tokens = TokenService(JWT_SECRET_KEY)

    with traced("init users"):
        users = UserService(store)

    with traced("init strava"):
        strava = StravaService(users)

    with traced("init response urls"):
        response_urls = ResponseUrlService(store, tokens)

    with traced("init lambda client"):
        lambda_client = boto3.client("lambda")

    with traced("init events"):
        events = EventService(STRAVA_EVENT_HANDLER, lambda_client)

    with traced("init slack"):
        slack = SlackService(app)

    with traced("init channel handler"):
        channel_handler = ChannelHandler(slack)

    with traced("init auth handler"):
        auth_handler = StravaAuthHandler(templates, users, strava, tokens, response_urls, AUTH_FLOW_TTL)

    with traced("init event handler"):
        event_handler = StravaEventHandler(events)

    with traced("setup creep command"):
        with api.command("/creep") as creep:
            creep.on("connect", "Connect to your Strava account")(auth_handler.handle_connect_command)
            creep.on("disconnect", "Disconnect your Strava account")(auth_handler.handle_disconnect_command)
            creep.on("kick", "Remove from the current channel")(channel_handler.handle_kick_command)

    with traced("setup auth action"):
        api.slack.action("authenticate_clicked")(auth_handler.handle_authenticate_action)  # type: ignore

    with traced("setup routes"):
        api.route("/strava/auth", methods=["GET"])(auth_handler.handle_strava_callback)
        api.route("/strava/auth", methods=["POST"])(auth_handler.handle_strava_connect)
        api.route("/strava/event", methods=["POST"])(event_handler.handle_webhook)
        api.route("/strava/event", methods=["GET"])(event_handler.handle_verify)

    return api
