from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

from stravabot.db import KeyValueStore


def _key(user_id: str) -> str:
    return f"user:{user_id}"


@dataclass
class UserAccessToken:
    token: str
    expires_at: int
    refresh_token: str


@dataclass
class User:
    strava_id: str
    slack_id: str
    strava_access_token: UserAccessToken

    @staticmethod
    def from_dict(data: dict) -> User:
        token = data["strava_access_token"]
        return User(
            strava_id=data["strava_id"],
            slack_id=data["slack_id"],
            strava_access_token=UserAccessToken(
                token=token["token"],
                expires_at=token["expires_at"],
                refresh_token=token["refresh_token"],
            ),
        )


class UserService:
    def __init__(self, store: KeyValueStore):
        self.store = store

    def put(self, user: User) -> None:
        self.store.put(
            key=_key(user.strava_id),
            value=asdict(user),
        )

    def get(self, user_id: str) -> Optional[User]:
        data = self.store.get(_key(user_id))
        if data is None:
            return None
        return User.from_dict(data)
