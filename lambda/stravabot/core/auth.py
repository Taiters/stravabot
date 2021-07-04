from datetime import timedelta
from typing import Callable

import requests

from stravabot import messages
from stravabot.api import ApiRequest, ApiResponse
from stravabot.models import User, UserAccessToken
from stravabot.services import strava
from stravabot.services.response_url import ResponseUrlService
from stravabot.services.strava import StravaAthleteCredentials
from stravabot.services.token import TokenService
from stravabot.services.user import UserService


def _create_user(athlete_credentials: StravaAthleteCredentials, slack_id: str) -> User:
    return User(
        strava_id=athlete_credentials.id,
        slack_id=slack_id,
        strava_access_token=UserAccessToken(
            token=athlete_credentials.access_token,
            refresh_token=athlete_credentials.refresh_token,
            expires_at=athlete_credentials.expires_at,
        ),
    )


class AuthFlow:
    def __init__(
        self,
        users: UserService,
        tokens: TokenService,
        response_urls: ResponseUrlService,
        auth_flow_ttl: timedelta,
    ):
        self.users = users
        self.tokens = tokens
        self.response_urls = response_urls
        self.auth_flow_ttl = auth_flow_ttl

    def send_oauth_url(self, ack: Callable, body: dict) -> None:
        token = self.response_urls.generate_token(body["user_id"], self.auth_flow_ttl)
        oauth_url = strava.get_oauth_url(token.token)
        ack(messages.connect_response(action_id="authenticate_clicked", token=token.token, oauth_url=oauth_url))

    def store_response_url(self, ack: Callable, body: dict, action: dict) -> None:
        token = self.tokens.decode(action["value"])
        response_url = body["response_url"]
        self.response_urls.put(token, response_url)
        ack()

    def handle_strava_callback(self, request: ApiRequest) -> ApiResponse:
        if "token" not in request.query_parameters:
            return ApiResponse.bad_request()

        token = self.tokens.decode(request.query_parameters["token"])
        response_url = self.response_urls.get(token)
        if response_url is None:
            return ApiResponse.bad_request()

        if "error" in request.query_parameters:
            requests.post(response_url, json=messages.connect_result(False))
            return ApiResponse(body="Denied")

        credentials = strava.get_athlete_credentials(request.query_parameters["code"])
        self.users.put(_create_user(credentials, token.slack_user_id))

        requests.post(response_url, json=messages.connect_result())
        return ApiResponse(body="GRAVY")

    def disconnect_user(self, ack: Callable, body: dict) -> None:
        user_id = body["user_id"]
        user = self.users.get_by_slack_id(user_id)

        if user is None:
            ack(messages.disconnect_response("Couldn't find you"))
        else:
            strava.deauthorize(user)
            ack(messages.disconnect_response())
