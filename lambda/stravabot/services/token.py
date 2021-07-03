from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from jose import jwt

from stravabot.utils import ttl_to_unixtime


@dataclass
class Token:
    slack_user_id: str
    data: dict
    token: str
    expires: Optional[int] = None


class TokenService:
    def __init__(self, secret: str):
        self.secret = secret

    def generate(self, user_id: str, data: dict = {}, ttl: timedelta = None) -> Token:
        data = data.copy()
        data["sub"] = user_id
        if ttl:
            data["exp"] = ttl_to_unixtime(ttl)
        return Token(
            slack_user_id=user_id,
            data=data,
            token=str(jwt.encode(data, self.secret)),
            expires=data.get("exp"),
        )

    def decode(self, token: str) -> Token:
        data = jwt.decode(token, self.secret)
        return Token(
            slack_user_id=data["sub"],
            data=data,
            token=token,
            expires=data.get("exp"),
        )
