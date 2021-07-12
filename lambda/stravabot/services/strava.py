import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from stravabot.clients import strava
from stravabot.models import StravaActivity, User, UserAccessToken
from stravabot.services.user import UserService


@dataclass
class StravaAthleteCredentials:
    id: int
    access_token: str
    refresh_token: str
    expires_at: int


class StravaSession:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def deauthorize(self) -> None:
        strava.deauthorize(self.access_token)

    def activity(self, id: int) -> StravaActivity:
        data = strava.activity(id, self.access_token)
        return StravaActivity.from_dict(data)


class StravaService:
    def __init__(self, users: UserService):
        self.users = users

    @contextmanager
    def session(self, user: User) -> Iterator[StravaSession]:
        current_token = user.strava_access_token
        if current_token.expires_at <= time.time():
            data = strava.oauth_token(refresh_token=user.strava_access_token.refresh_token)
            current_token = UserAccessToken(
                token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=int(data["expires_at"]),
            )
            user.strava_access_token = current_token
            self.users.put(user)
        yield StravaSession(current_token.token)

    def get_oauth_url(self, token: str) -> str:
        return strava.oauth_url(token)

    def get_athlete_credentials(self, code: str) -> StravaAthleteCredentials:
        data = strava.oauth_token(code=code)
        return StravaAthleteCredentials(
            id=int(data["athlete"]["id"]),
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=int(data["expires_at"]),
        )
