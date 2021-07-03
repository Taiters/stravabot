import boto3

from stravabot.api import Api
from stravabot.config import JWT_SECRET_KEY, KV_STORE_TABLE
from stravabot.config.base import AUTH_FLOW_TTL
from stravabot.core.auth import AuthFlow
from stravabot.db import KeyValueStore
from stravabot.services.response_url import ResponseUrlService
from stravabot.services.token import TokenService
from stravabot.services.user import UserService


def bootstrap() -> Api:
    api = Api()
    dynamodb = boto3.resource("dynamodb")
    store = KeyValueStore(dynamodb.Table(KV_STORE_TABLE))
    tokens = TokenService(JWT_SECRET_KEY)
    users = UserService(store)
    response_urls = ResponseUrlService(store, tokens)

    auth_flow = AuthFlow(users, tokens, response_urls, AUTH_FLOW_TTL)

    with api.command("/creep") as creep:
        creep.on("connect", "Connect to your Strava account")(auth_flow.send_oauth_url)

    api.slack.action("authenticate_clicked")(auth_flow.store_response_url)  # type: ignore
    api.route("/strava/auth", methods=["GET"])(auth_flow.handle_strava_callback)

    return api
