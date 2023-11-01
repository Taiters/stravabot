from uuid import uuid4
from django.utils import timezone
from django.conf import settings
import jwt


class JWTOAuthStateStore:
    expiration_time_seconds: int

    def __init__(self, expiration_seconds: int):
        self.expiration_seconds = expiration_seconds

    def issue(self, extra_fields={}) -> str:
        state = jwt.encode(
            {
                "exp": timezone.now() + timezone.timedelta(seconds=self.expiration_seconds),
                "state": str(uuid4()),
                **extra_fields,
            },
            settings.SECRET_KEY,
            algorithm='HS256',
        )
        return state
    
    def decode(self, state: str) -> dict:
        return jwt.decode(
            state,
            settings.SECRET_KEY,
            algorithms=['HS256'],
            options={
                'require': ['exp', 'state']
            }
        )

    def consume(self, state: str) -> bool:
        try:
            self.decode(state)
        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError, jwt.DecodeError):
            return False
        return True