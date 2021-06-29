from datetime import timedelta

from jose import jwt

from stravabot.utils import ttl_to_unixtime
from stravabot.config import JWT_SECRET_KEY


def generate_token(user_id: str, claims: dict = {}, ttl: timedelta = None):
    claims["sub"] = user_id
    if ttl:
        claims["exp"] = ttl_to_unixtime(ttl)
    return str(jwt.encode(claims, JWT_SECRET_KEY))


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET_KEY)
