from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


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


@dataclass
class Token:
    slack_user_id: str
    data: dict
    token: str
    expires: Optional[int] = None
