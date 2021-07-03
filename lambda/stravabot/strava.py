from urllib.parse import urlencode

import requests

from stravabot.config import STRAVA_CALLBACK_URL, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET

BASE_URL = "https://www.strava.com"


def get_oauth_url(token):
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "redirect_uri": f"{STRAVA_CALLBACK_URL}?token={token}",
        "response_type": "code",
        "scope": "read,activity:read",
    }
    return f"{BASE_URL}/oauth/authorize?{urlencode(params)}"


def exchange_token(token: str) -> dict:
    response = requests.post(
        f"{BASE_URL}/api/v3/oauth/token",
        json={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "code": token,
            "grant_type": "authorization_code",
        },
    )
    return response.json()
