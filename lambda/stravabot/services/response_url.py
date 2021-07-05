from datetime import timedelta
from typing import Optional
from uuid import uuid4

from stravabot.db import KeyValueStore
from stravabot.services.token import Token, TokenService


def _key(user_id: str, response_id: str) -> str:
    return f"response_id:{user_id}:{response_id}"


class ResponseUrlService:
    def __init__(self, store: KeyValueStore, tokens: TokenService):
        self.store = store
        self.tokens = tokens

    def generate_token(self, user_id: str, ttl: timedelta) -> Token:
        return self.tokens.generate(
            user_id=user_id,
            data={"response_id": str(uuid4())},
            ttl=ttl,
        )

    def put(self, token: Token, response_url: str) -> None:
        self.store.put(
            key=_key(token.slack_user_id, token.data["response_id"]),
            value={"response_url": response_url},
            expires=token.expires,
        )

    def get(self, token: Token) -> Optional[str]:
        result = self.store.get(_key(token.slack_user_id, token.data["response_id"]), consistent_read=True)
        return result.get("response_url") if result else None
