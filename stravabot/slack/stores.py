from datetime import datetime, timedelta, tzinfo
import logging
from uuid import UUID
from django.utils import timezone
from slack_sdk.oauth.state_store import OAuthStateStore

from stravabot.models import SlackAuthState

class StravabotSlackOAuthStateStore(OAuthStateStore):
    def __init__(
        self,
        *,
        expiration_seconds: int,
    ):
        self.expiration_seconds = expiration_seconds

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    def issue(self, *args, **kwargs) -> str:
        auth_state = SlackAuthState.objects.create()
        return str(auth_state.state)

    def consume(self, state: str) -> bool:
        existing_state = SlackAuthState.objects.get(state=UUID(state))
        expires_at = existing_state.created_at + timedelta(seconds=self.expiration_seconds)
        still_valid = expires_at > timezone.now()
        existing_state.delete()
        return still_valid
