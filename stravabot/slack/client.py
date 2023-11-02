from typing import Optional
from django.conf import settings
from slack_sdk import WebClient
from .stores import DjangoInstallationStore
from slack_sdk.oauth.token_rotation.rotator import TokenRotator

installation_store = DjangoInstallationStore()
token_rotator = TokenRotator(client_id=settings.SLACK_CLIENT_ID, client_secret=settings.SLACK_CLIENT_SECRET)


def get_slack_client(team_id: Optional[str], enterprise_id: Optional[str]) -> WebClient:
    bot = installation_store.find_bot(team_id=team_id, enterprise_id=enterprise_id)
    rotated_bot = token_rotator.perform_bot_token_rotation(bot=bot)
    if rotated_bot is not None:
        installation_store.save_bot(rotated_bot)
        bot = rotated_bot
    return WebClient(bot.bot_token)