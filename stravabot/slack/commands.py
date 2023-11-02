from typing import Callable
from stravalib import Client
from django.conf import settings

from ..oauth.store import JWTOAuthStateStore

strava_client = Client()
state_store = JWTOAuthStateStore(expiration_seconds=120)

def connect(ack, context, command, body, client):
    ack()
    response = client.views_open(
        trigger_id=body['trigger_id'],
        view={
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Connect to Strava",
                "emoji": True
            },
            "blocks": [],
        } 
    )
    view_id = response['view']['id']

    state = state_store.issue(extra_fields={
        'enterprise_id': context['enterprise_id'],
        'team_id': context['team_id'],
        'user_id': command['user_id'],
        'view_id': view_id,
    })
    authorize_url = strava_client.authorization_url(
        client_id=settings.STRAVA_CLIENT_ID,
        redirect_uri=settings.BASE_URL + "/strava/oauth_redirect",
        state=state,
    )

    client.views_update(
        view_id=view_id,
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
                        "text": f"*Hi <@{command['user_id']}>!*",
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Click to connect to your Strava account"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Connect",
                            "emoji": True
                        },
                        "style": "primary",
                        "url": authorize_url,
                    }
                }
            ]
        }
    )

def disconnect(ack):
    ack("disconnect")

def kick(ack):
    ack("kick")

def setup_commands(command: Callable[[str, str], Callable]):
    command("connect", "Connect to Strava")(connect)
    command("disconnect", "Disconnect from Strava")(disconnect)
    command("kick", "Kick me")(kick)
