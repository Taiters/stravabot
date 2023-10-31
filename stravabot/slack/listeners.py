from collections import namedtuple
import logging
from typing import Callable

from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings

from django.conf import settings

from .commands import setup_commands
from .stores import DjangoInstallationStore, DjangoOAuthStateStore

logger = logging.getLogger(__name__)

app = App(
    signing_secret=settings.SLACK_SIGNING_SECRET,
    oauth_settings=OAuthSettings(
        client_id=settings.SLACK_CLIENT_ID,
        client_secret=settings.SLACK_CLIENT_SECRET,
        installation_store=DjangoInstallationStore(),
        state_store=DjangoOAuthStateStore(expiration_seconds=120),
        redirect_uri=settings.BASE_URL+'/slack/oauth_redirect',
        user_scopes=[],
        scopes=[
            'channels:join',
            'channels:manage',
            'channels:read',
            'chat:write',
            'commands',
            'groups:read',
            'groups:write',
        ],
    ),
)


def _match_name(name) -> Callable[[dict], bool]:
    def match(command: dict) -> bool:
        if "text" not in command:
            return False
        return command["text"].strip().lower().startswith(name)

    return match

Command = namedtuple('Command', ['name', 'help_text'])
commands = []
def command_decorator_factory(name, help_text):
    def decorator(f):
        commands.append(Command(name, help_text))
        app.command(f"/{settings.BOT_NAME}", matchers=[_match_name(name)])(f)
    return decorator
setup_commands(command_decorator_factory)

@app.command(f"/{settings.BOT_NAME}")
def help(ack):
    ack({
        "blocks": [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Available commands"
                    }
                ]
            },
        ] + [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"`{c.name}`\n\t\t{c.help_text}"
                    }
                ]
            }
            for c in commands
        ],
    })