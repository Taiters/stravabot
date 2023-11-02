import logging
from typing import Optional
from django.conf import settings
from django.db.models import F
from django.utils.timezone import is_naive, make_aware
from slack_sdk.oauth import InstallationStore, OAuthStateStore
from slack_sdk.oauth.installation_store import Bot, Installation

from .models import SlackBot
from ..oauth.store import JWTOAuthStateStore


class DjangoInstallationStore(InstallationStore):
    def __init__(
        self,
    ):
        self._logger = logging.getLogger(__name__)

    @property
    def logger(self):
        return self._logger

    def save(self, installation: Installation):
        self.save_bot(installation.to_bot())

    def save_bot(self, bot: Bot):
        b = bot.to_dict()

        del b['app_id']

        if is_naive(b["installed_at"]):
            b["installed_at"] = make_aware(b["installed_at"])
        if b.get("bot_token_expires_at") is not None and is_naive(b["bot_token_expires_at"]):
            b["bot_token_expires_at"] = make_aware(b["bot_token_expires_at"])

        SlackBot.objects.update_or_create(
            enterprise_id=bot.enterprise_id,
            team_id=bot.team_id,
            defaults=b,
        )

    def find_bot(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        e_id = enterprise_id or None
        t_id = team_id or None
        if is_enterprise_install:
            t_id = None
        rows = SlackBot.objects.filter(enterprise_id=e_id, team_id=t_id)
        if len(rows) > 0:
            b = rows[0]
            return Bot(
                app_id=settings.SLACK_APP_ID,
                enterprise_id=b.enterprise_id,
                team_id=b.team_id,
                bot_token=b.bot_token,
                bot_refresh_token=b.bot_refresh_token,
                bot_token_expires_at=b.bot_token_expires_at,
                bot_id=b.bot_id,
                bot_user_id=b.bot_user_id,
                bot_scopes=b.bot_scopes,
                installed_at=b.installed_at,
            )
        return None


class DjangoOAuthStateStore(JWTOAuthStateStore, OAuthStateStore):
    def __init__(
        self,
        expiration_seconds: int,
    ):
        self._logger = logging.getLogger(__name__)
        super().__init__(expiration_seconds)

    @property
    def logger(self):
        return self._logger
