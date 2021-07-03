from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from stravabot.db import KeyValueStore
from stravabot.models import User


def _key(user_id: str) -> str:
    return f"user:{user_id}"


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
