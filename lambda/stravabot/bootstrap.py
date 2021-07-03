from datetime import timedelta

import boto3
import requests

from stravabot import messages, strava
from stravabot.api import Api, ApiRequest, ApiResponse
from stravabot.config import JWT_SECRET_KEY, KV_STORE_TABLE
from stravabot.db import KeyValueStore
from stravabot.services.response_url import ResponseUrlService
from stravabot.services.token import TokenService
from stravabot.services.user import User, UserAccessToken, UserService


def bootstrap() -> Api:
    api = Api()
    dynamodb = boto3.resource("dynamodb")
    store = KeyValueStore(dynamodb.Table(KV_STORE_TABLE))
    tokens = TokenService(JWT_SECRET_KEY)
    users = UserService(store)
    response_urls = ResponseUrlService(store, tokens)

    with api.command("/creep") as creep:

        @creep.on("connect", "Connect to your Strava account")
        def connect(body, ack):
            token = response_urls.generate_token(body["user_id"], timedelta(minutes=10))
            oauth_url = strava.get_oauth_url(token.token)
            ack(messages.connect_response(action_id="authenticate_clicked", token=token.token, oauth_url=oauth_url))

    @api.slack.action("authenticate_clicked")  # type: ignore
    def authenticate_clicked(ack, action, body):
        token = tokens.decode(action["value"])
        response_url = body["response_url"]
        response_urls.put(token, response_url)
        ack()

    @api.route("/strava/auth", methods=["GET"])
    def strava_auth(request: ApiRequest) -> ApiResponse:
        if "token" not in request.query_parameters:
            return ApiResponse.bad_request()

        token = tokens.decode(request.query_parameters["token"])
        response_url = response_urls.get(token)
        if response_url is None:
            return ApiResponse.bad_request()

        if "error" in request.query_parameters:
            requests.post(response_url, messages.connect_result(False))
            return ApiResponse(body="Denied")

        code = request.query_parameters["code"]
        strava_data = strava.exchange_token(code)
        athlete = strava_data["athlete"]
        users.put(
            User(
                strava_id=athlete["id"],
                slack_id=token.slack_user_id,
                strava_access_token=UserAccessToken(
                    token=strava_data["access_token"],
                    refresh_token=strava_data["refresh_token"],
                    expires_at=strava_data["expires_at"],
                ),
            )
        )

        requests.post(response_url, messages.connect_result())
        return ApiResponse(body="Gravy")

    return api
