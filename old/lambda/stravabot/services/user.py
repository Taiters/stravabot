from __future__ import annotations

from dataclasses import asdict
from typing import Optional

from stravabot.db import KeyValueStore, KeyValueStoreIndex
from stravabot.models import User


def _key(user_id: int) -> str:
    return f"user:{user_id}"


class UserService:
    def __init__(self, store: KeyValueStore):
        self.store = store

    def put(self, user: User) -> None:
        self.store.put(
            key=_key(user.strava_id),
            value=asdict(user),
        )

    def get_by_slack_id(self, user_id: str) -> Optional[User]:
        return self._get(user_id, index=KeyValueStoreIndex.SLACK_ID)

    def get_by_strava_id(self, user_id: int) -> Optional[User]:
        return self._get(_key(user_id))

    def _get(self, key: str, index: Optional[KeyValueStoreIndex] = None) -> Optional[User]:
        data = self.store.get(key, index=index)
        if data is None:
            return None
        return User.from_dict(data)

    def delete(self, user_id: int) -> None:
        self.store.delete(_key(user_id))
