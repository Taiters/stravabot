from typing import Callable
from stravalib import Client
from django.conf import settings

strava_client = Client()

def connect(ack, command):
    authorize_url = strava_client.authorization_url(
        client_id=settings.STRAVA_CLIENT_ID, redirect_uri=settings.BASE_URL + "/strava/oauth_redirect",
    )
    user_id = command['user_id']
    ack(
        {
            "response_type": "ephemeral",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Hi <@{user_id}> :wave:"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Can't wait to get you set up!",
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "In order to get started, click the botton below to connect your Strava account",
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Connect to Strava",
                                "emoji":True,
                            },
                            "style": "primary",
                            "action_id": "authenticate_strava",
                            "url": authorize_url,
                        }
                    ]
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