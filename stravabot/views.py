from django.conf import settings
from django.http import HttpResponse

from stravabot.slack.models import SlackBot

from stravabot.models import User

from stravabot.slack.client import get_slack_client
from stravabot.strava.client import get_strava_client
from stravabot.oauth.store import JWTOAuthStateStore

state_store = JWTOAuthStateStore()


def strava_oauth_redirect(request):
    code = request.GET['code']
    state = state_store.decode(request.GET['state'])
    enterprise_id = state['enterprise_id']
    team_id = state['team_id']
    slack_user_id = state['user_id']
    view_id = state['view_id']

    strava = get_strava_client()
    token_response = strava.exchange_code_for_token(
        client_id=settings.STRAVA_CLIENT_ID,
        client_secret=settings.STRAVA_CLIENT_SECRET,
        code=code,
    )
    strava.access_token = token_response['access_token']
    athlete = strava.get_athlete()

    user = User.objects.update_or_create(strava_athlete_id=athlete.id, defaults={
        'strava_access_token': token_response['access_token'],
        'strava_refresh_token': token_response['refresh_token'],
        'strava_token_expires_at': token_response['expires_at'],
    })
    slack_bot = SlackBot.objects.get(team_id=team_id, enterprise_id=enterprise_id)
    slack_bot.users.add(user)

    slack = get_slack_client(team_id=team_id, enterprise_id=enterprise_id)
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
