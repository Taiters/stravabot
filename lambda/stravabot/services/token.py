from datetime import timedelta
from typing import Optional

import jwt

from stravabot.models import Token
from stravabot.utils import ttl_to_unixtime


class TokenService:
    def __init__(self, secret: str):
        self.secret = secret

    def generate(self, user_id: str, data: dict = {}, ttl: Optional[timedelta] = None) -> Token:
        data = data.copy()
        data["sub"] = user_id
        if ttl:
            data["exp"] = ttl_to_unixtime(ttl)
        return Token(
            slack_user_id=user_id,
            data=data,
            token=str(jwt.encode(data, self.secret, "HS256")),
            expires=data.get("exp"),
        )

    def decode(self, token: str) -> Token:
        data = jwt.decode(token, self.secret, ["HS256"])
        return Token(
            slack_user_id=data["sub"],
            data=data,
            token=token,
            expires=data.get("exp"),
        )
