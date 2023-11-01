from uuid import uuid4
from django.http import HttpResponse
from slack_sdk import WebClient
from stravabot.oauth.store import JWTOAuthStateStore

from stravabot.slack.stores import DjangoInstallationStore

installation_store = DjangoInstallationStore()
state_store = JWTOAuthStateStore(expiration_seconds=120)

def strava_oauth_redirect(request):
    state = state_store.decode(request.GET['state'])
    bot = installation_store.find_bot(enterprise_id=None, team_id=state['team_id'])
    slack = WebClient(token=bot.bot_token)
    slack.views_update(
        view_id=state['view_id'],
        view={
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Connect to Strava",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Hi <@{state['user_id']}>!*",
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Absolutely smashed it!"
                    },
                }
            ]
        }
    )
    return HttpResponse("Got here anyway, check Slack")

def slack_install_redirect(request):
    request.session["slack_oauth_state"] = str(uuid4())