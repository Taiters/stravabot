import pytest
from unittest.mock import patch
from django.utils import timezone
from django.conf import settings
from slack_sdk.oauth.installation_store import Installation

from stravabot.slack.stores import DjangoInstallationStore, DjangoOAuthStateStore


def test_issue_and_consume():
    store = DjangoOAuthStateStore(120)
    state = store.issue()
    assert store.consume(state)

@pytest.mark.parametrize('time_since_created,should_pass', [
    (120, False),
    (121, False),
    (119, True),
    (1, True),
    (240, False),
])
def test_consume_expired(time_since_created, should_pass):
    time_in_past = timezone.now() - timezone.timedelta(seconds=time_since_created)
    with patch('stravabot.oauth.store.timezone.now') as now_mock:
        now_mock.return_value = time_in_past
        store = DjangoOAuthStateStore(120)
        state = store.issue()
    assert store.consume(state) == should_pass

def test_consume_modified():
    store = DjangoOAuthStateStore(120)
    state = store.issue() + "modified"
    assert store.consume(state) == False

@pytest.mark.django_db
def test_store_team_installation():
    installation_store = DjangoInstallationStore()
    installation_store.save(Installation(
        app_id=settings.SLACK_APP_ID,
        team_id='team_id',
        team_name='team_name',
        bot_token='bot_token',
        bot_id='bot_id',
        bot_user_id='bot_user_id',
        bot_scopes=['a', 'b', 'c'],
        bot_refresh_token='bot_refresh_token',
        bot_token_expires_in=1234,
        bot_token_expires_at=5678,
        user_id='user_id',
        user_token='user_token',
        user_scopes=['d', 'e', 'f'],
        user_refresh_token='user_refresh_token',
        user_token_expires_in=91011,
        user_token_expires_at=8999,
        incoming_webhook_url='incoming_webhook_url',
        incoming_webhook_channel='incoming_channel',
        incoming_webhook_channel_id='incoming_channel_id',
        incoming_webhook_configuration_url='incoming_config_url',
        is_enterprise_install=False,
        token_type='token_type',
        installed_at=timezone.datetime(year=2023, month=1, day=23),
    ))

    bot = installation_store.find_bot(enterprise_id=None, team_id='team_id')

    assert bot is not None