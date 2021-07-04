from dataclasses import dataclass

from stravabot.clients import strava
from stravabot.models import User


@dataclass
class StravaAthleteCredentials:
    id: str
    access_token: str
    refresh_token: str
    expires_at: int


def get_oauth_url(token: str) -> str:
    return strava.oauth_url(token)


def get_athlete_credentials(code: str) -> StravaAthleteCredentials:
    data = strava.oauth_token(code=code)
    return StravaAthleteCredentials(
        id=data["athlete"]["id"],
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_at=data["expires_at"],
    )


def deauthorize(user: User) -> None:
    strava.deauthorize(user.strava_access_token.token)
