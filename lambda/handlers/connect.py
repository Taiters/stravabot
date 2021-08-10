import boto3
import requests
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from stravabot.api import ApiRequest, api_endpoint, bad_request
from stravabot.clients.strava import InvalidStravaTokenError
from stravabot.config import JWT_SECRET_KEY, KV_STORE_TABLE
from stravabot.db import KeyValueStore
from stravabot.messages import context, mrkdwn, response
from stravabot.models import User, UserAccessToken
from stravabot.services.response_url import ResponseUrlService
from stravabot.services.strava import StravaAthleteCredentials, StravaService
from stravabot.services.token import TokenService
from stravabot.services.user import UserService

dynamodb = boto3.resource("dynamodb")
store = KeyValueStore(dynamodb.Table(KV_STORE_TABLE))
tokens = TokenService(JWT_SECRET_KEY)
users = UserService(store)
strava = StravaService(users)
response_urls = ResponseUrlService(store, tokens)


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


@api_endpoint
def handler(request: ApiRequest) -> dict:
    data = request.json()
    if "token" not in data or "code" not in data:
        return bad_request()

    try:
        token = tokens.decode(data["token"])
    except ExpiredSignatureError:
        return bad_request(
            {
                "message": "Token expired",
            }
        )
    except InvalidTokenError:
        return bad_request()

    try:
        credentials = strava.get_athlete_credentials(data["code"])
    except InvalidStravaTokenError:
        return bad_request()

    users.put(_create_user(credentials, token.slack_user_id))
    response_url = response_urls.get(token, max_attempts=3)
    if response_url is not None:
        requests.post(
            response_url,
            json=response(
                context(mrkdwn("Connected to Strava")),
                replace_original=True,
            ),
        )

    return {"statusCode": 200}
