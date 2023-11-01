from unittest.mock import patch
import pytest
from django.urls import reverse
from django.test import Client
from slack_sdk.oauth import OAuthStateUtils
from stravabot.slack.stores import DjangoOAuthStateStore, DjangoInstallationStore


@pytest.mark.django_db
@patch('stravabot.slack.listeners.app.oauth_flow.client.auth_test')
@patch('stravabot.slack.listeners.app.oauth_flow.client.oauth_v2_access')
def test_authorize(mock_oauth_v2_access, mock_auth_test):
    mock_oauth_v2_access.return_value = {
        "ok": True,
        "access_token": "the-access-token",
        "refresh_token": "the-refresh-token",
        "token_type": "bot",
        "scope": "commands,incoming-webhook",
        "bot_user_id": "the-bot-user-id",
        "app_id": "the-app-id",
        "team": {
            "name": "The team name",
            "id": "the-team-id"
        },
        "authed_user": {
            "id": "the-authed-user",
            "access_token": "the-authed-user-access-token",
            "token_type": "user"
        }
    }
    mock_auth_test.return_value = {
        'bot_id': 'the-bot-id',
    }
    client = Client()
    installation_store = DjangoInstallationStore()
    state = DjangoOAuthStateStore(expiration_seconds=120).issue()
    client.cookies[OAuthStateUtils.default_cookie_name] = state

    result = client.get(reverse('slack_authorize'), {
        'code': 'abcd',
        'state': state,
    })

    assert result.status_code == 200

    installation = installation_store.find_installation(enterprise_id=None, team_id='the-team-id', user_id='the-authed-user')
    bot = installation_store.find_bot(enterprise_id=None, team_id='the-team-id')

    assert installation.bot_token == 'the-access-token'
    assert installation.bot_refresh_token == 'the-refresh-token'
    assert bot.bot_token == 'the-access-token'
    assert bot.bot_refresh_token == 'the-refresh-token'