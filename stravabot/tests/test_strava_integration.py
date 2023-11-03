from unittest.mock import ANY, Mock, patch
from django.urls import reverse
from django.utils import timezone
import pytest
from django.test import Client
from stravabot.models import User

from stravabot.oauth.store import JWTOAuthStateStore
from stravabot.slack.models import SlackBot

@pytest.mark.django_db
@patch('stravabot.views.get_strava_client')
@patch('stravabot.views.get_slack_client')
def test_authorize(mock_get_slack_client, mock_get_strava_client):
    SlackBot.objects.create(
        team_id='a-team-id',
        bot_token='some-token',
    )
    state = JWTOAuthStateStore().issue({
        'user_id': 'a-user-id',
        'team_id': 'a-team-id',
        'enterprise_id': None,
        'view_id': 'a-view-id',
    })
    mock_slack_client = mock_get_slack_client.return_value
    mock_strava_client = mock_get_strava_client.return_value

    strava_token_expiration_time = int((timezone.now() + timezone.timedelta(days=30)).timestamp())
    mock_strava_client.exchange_code_for_token.return_value = {
        'access_token': 'strava-access-token',
        'refresh_token': 'strava-refresh-token',
        'expires_at': strava_token_expiration_time
    }
    mock_strava_client.get_athlete.return_value.id = 'strava-athlete-id'
    client = Client()

    response = client.get(reverse('strava_authorize'), {
        'code': 'abcd',
        'state': state,
    })

    assert response.status_code == 200

    user = User.objects.get(strava_athlete_id='strava-athlete-id')
    assert user.strava_access_token == 'strava-access-token'
    assert user.strava_refresh_token == 'strava-refresh-token'
    assert user.strava_token_expires_at.timestamp() == strava_token_expiration_time

    mock_get_slack_client.assert_called_once_with(
        team_id='a-team-id',
        enterprise_id=None,
    )
    mock_slack_client.views_update.assert_called_once_with(
        view_id='a-view-id',
        view=ANY,
    )