from datetime import timedelta
from typing import Callable

import requests
from jinja2 import Environment
from jose.exceptions import ExpiredSignatureError, JWTError

from stravabot import messages
from stravabot.api import ApiRequest, ApiResponse
from stravabot.clients.strava import InvalidTokenError
from stravabot.config import HOST
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


class StravaAuthHandler:
    def __init__(
        self,
        templates: Environment,
        users: UserService,
        tokens: TokenService,
        response_urls: ResponseUrlService,
        auth_flow_ttl: timedelta,
    ):
        self.templates = templates
        self.users = users
        self.tokens = tokens
        self.response_urls = response_urls
        self.auth_flow_ttl = auth_flow_ttl

    def handle_connect_command(self, ack: Callable, body: dict) -> None:
        token = self.response_urls.generate_token(body["user_id"], self.auth_flow_ttl)
        oauth_url = strava.get_oauth_url(token.token)
        ack(messages.connect_response(action_id="authenticate_clicked", token=token.token, oauth_url=oauth_url))

    def handle_disconnect_command(self, ack: Callable, body: dict) -> None:
        user_id = body["user_id"]
        user = self.users.get_by_slack_id(user_id)

        if user is None:
            ack(
                messages.disconnect_response(
                    "What is this!? I can't find you. You can't disconnect without connecting. Maybe you should connect instead..."
                )
            )
        else:
            strava.deauthorize(user)
            ack(messages.disconnect_response())

    def handle_authenticate_action(self, ack: Callable, body: dict, action: dict) -> None:
        token = self.tokens.decode(action["value"])
        response_url = body["response_url"]
        self.response_urls.put(token, response_url)
        ack()

    def handle_strava_connect(self, request: ApiRequest) -> ApiResponse:
        data = request.json()
        if "token" not in data or "code" not in data:
            return ApiResponse.bad_request()

        try:
            token = self.tokens.decode(data["token"])
        except ExpiredSignatureError:
            return ApiResponse.bad_request(
                {
                    "message": "Token expired",
                }
            )
        except JWTError:
            return ApiResponse.bad_request()

        try:
            credentials = strava.get_athlete_credentials(data["code"])
        except InvalidTokenError:
            return ApiResponse.bad_request()

        self.users.put(_create_user(credentials, token.slack_user_id))
        response_url = self.response_urls.get(token, max_attempts=3)
        if response_url is not None:
            requests.post(response_url, json=messages.connect_result())

        return ApiResponse.ok()

    def handle_strava_callback(self, request: ApiRequest) -> ApiResponse:
        template = self.templates.get_template("auth.html")
        return ApiResponse(
            body=template.render(
                host=HOST,
                parameters={
                    "error": request.query_parameters.get("error"),
                    "token": request.query_parameters.get("token"),
                    "code": request.query_parameters.get("code"),
                },
            ),
            headers={
                "Content-Type": "text/html",
            },
        )