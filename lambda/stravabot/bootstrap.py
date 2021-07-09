import boto3
from jinja2 import Environment, PackageLoader, select_autoescape
from slack_bolt import App

from stravabot.api import Api
from stravabot.config import JWT_SECRET_KEY, KV_STORE_TABLE, STRAVA_EVENT_HANDLER
from stravabot.config.base import AUTH_FLOW_TTL
from stravabot.db import KeyValueStore
from stravabot.handlers import StravaAuthHandler, StravaEventHandler
from stravabot.services.event import EventService
from stravabot.services.response_url import ResponseUrlService
from stravabot.services.strava import StravaService
from stravabot.services.token import TokenService
from stravabot.services.user import UserService


def bootstrap() -> Api:
    templates = Environment(
        loader=PackageLoader("stravabot"),
        autoescape=select_autoescape(),
    )
    slack = App(process_before_response=True)
    api = Api(slack)
    dynamodb = boto3.resource("dynamodb")
    store = KeyValueStore(dynamodb.Table(KV_STORE_TABLE))

    tokens = TokenService(JWT_SECRET_KEY)
    users = UserService(store)
    strava = StravaService(users)
    response_urls = ResponseUrlService(store, tokens)
    events = EventService(STRAVA_EVENT_HANDLER, boto3.client("lambda"))

    auth_handler = StravaAuthHandler(templates, users, strava, tokens, response_urls, AUTH_FLOW_TTL)
    with api.command("/creep") as creep:
        creep.on("connect", "Connect to your Strava account")(auth_handler.handle_connect_command)
        creep.on("disconnect", "Disconnect your Strava account")(auth_handler.handle_disconnect_command)

    api.slack.action("authenticate_clicked")(auth_handler.handle_authenticate_action)  # type: ignore
    api.route("/strava/auth", methods=["GET"])(auth_handler.handle_strava_callback)
    api.route("/strava/auth", methods=["POST"])(auth_handler.handle_strava_connect)

    event_handler = StravaEventHandler(events)
    api.route("/strava/event", methods=["POST"])(event_handler.handle_webhook)
    api.route("/strava/event", methods=["GET"])(event_handler.handle_verify)

    return api
