from typing import Optional
from urllib.parse import urlencode

import requests

from stravabot.config import STRAVA_CALLBACK_URL, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET

BASE_URL = "https://www.strava.com"


class StravaUnauthorizedError(Exception):
    pass


def oauth_url(token: str) -> str:
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "redirect_uri": f"{STRAVA_CALLBACK_URL}?token={token}",
        "response_type": "code",
        "scope": "read,activity:read",
    }
    return f"{BASE_URL}/oauth/authorize?{urlencode(params)}"


def oauth_token(code: Optional[str] = None, refresh_token: Optional[str] = None) -> dict:
    data = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
    }
    if code is not None:
        data["code"] = code
        data["grant_type"] = "authorization_code"
    elif refresh_token is not None:
        data["refresh_token"] = refresh_token
        data["grant_type"] = "refresh_token"
    else:
        raise ValueError("Must pass either 'code' or 'refresh_token'")
    response = requests.post(f"{BASE_URL}/api/v3/oauth/token", json=data)
    return response.json()


def deauthorize(access_token: str) -> None:
    response = requests.post(f"{BASE_URL}/oauth/deauthorize", params={"access_token": access_token})
    if response.status_code == 401:
        raise StravaUnauthorizedError()


def athlete(access_token: str) -> dict:
    response = requests.get(
        f"{BASE_URL}/api/v3/athlete",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    return response.json()
