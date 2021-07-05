import boto3
from slack_bolt import App

from stravabot.api import Api
from stravabot.config import JWT_SECRET_KEY, KV_STORE_TABLE, STRAVA_EVENT_HANDLER
from stravabot.config.base import AUTH_FLOW_TTL
from stravabot.core import events
from stravabot.core.auth import AuthFlow
from stravabot.core.forwarder import ApiRequestForwarder
from stravabot.db import KeyValueStore
from stravabot.services.response_url import ResponseUrlService
from stravabot.services.token import TokenService
from stravabot.services.user import UserService


def bootstrap() -> Api:
    slack = App(process_before_response=True)
    api = Api(slack)
    dynamodb = boto3.resource("dynamodb")
    store = KeyValueStore(dynamodb.Table(KV_STORE_TABLE))
    tokens = TokenService(JWT_SECRET_KEY)
    users = UserService(store)
    response_urls = ResponseUrlService(store, tokens)

    auth_flow = AuthFlow(users, tokens, response_urls, AUTH_FLOW_TTL)
    api_request_forwarder = ApiRequestForwarder(STRAVA_EVENT_HANDLER, boto3.client("lambda"))

    with api.command("/creep") as creep:
        creep.on("connect", "Connect to your Strava account")(auth_flow.send_oauth_url)
        creep.on("disconnect", "Disconnect your Strava account")(auth_flow.disconnect_user)

    api.slack.action("authenticate_clicked")(auth_flow.store_response_url)  # type: ignore
    api.route("/strava/auth", methods=["GET"])(auth_flow.handle_strava_callback)
    api.route("/strava/event", methods=["POST"])(api_request_forwarder)
    api.route("/strava/event", methods=["GET"])(events.verify)

    return api
