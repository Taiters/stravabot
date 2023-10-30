import logging

from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings

from django.conf import settings

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


@app.command("/hello-django-app")
def command(ack):
    ack(":wave: Hello from a Django app :smile:")