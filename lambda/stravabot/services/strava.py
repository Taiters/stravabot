from dataclasses import dataclass
from urllib.parse import urlencode

import requests

from stravabot.config import STRAVA_CALLBACK_URL, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET

BASE_URL = "https://www.strava.com"


@dataclass
class StravaAthleteCredentials:
    id: str
    access_token: str
    refresh_token: str
    expires_at: int


def get_oauth_url(token: str) -> str:
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "redirect_uri": f"{STRAVA_CALLBACK_URL}?token={token}",
        "response_type": "code",
        "scope": "read,activity:read",
    }
    return f"{BASE_URL}/oauth/authorize?{urlencode(params)}"


def get_athlete_credentials(token: str) -> StravaAthleteCredentials:
    response = requests.post(
        f"{BASE_URL}/api/v3/oauth/token",
        json={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "code": token,
            "grant_type": "authorization_code",
        },
    )
    data = response.json()
    return StravaAthleteCredentials(
        id=data["athlete"]["id"],
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_at=data["expires_at"],
    )
