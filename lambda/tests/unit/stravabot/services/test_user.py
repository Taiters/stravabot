import pytest

from stravabot.db import KeyValueStoreIndex
from stravabot.models import User, UserAccessToken
from stravabot.services.user import UserService


@pytest.fixture
def store(mocker):
    return mocker.Mock()


@pytest.fixture
def user_service(store):
    return UserService(store)


def test_put_passes_expected_data_to_db(user_service, store):
    user_service.put(
        User(
            strava_id=1234,
            slack_id="abcd",
            strava_access_token=UserAccessToken(
                token="the-token",
                expires_at=1234567,
                refresh_token="the-refresh-token",
            ),
        )
    )
    store.put.assert_called_once_with(
        key="user:1234",
        value={
            "strava_id": 1234,
            "slack_id": "abcd",
            "strava_access_token": {
                "token": "the-token",
                "expires_at": 1234567,
                "refresh_token": "the-refresh-token",
            },
        },
    )


def test_get_by_strava_id_returns_expected_user_from_db(user_service, store):
    store.get.return_value = {
        "strava_id": 1234,
        "slack_id": "slack",
        "strava_access_token": {
            "token": "another-token",
            "expires_at": 767676,
            "refresh_token": "another-refresh-token",
        },
    }
    result = user_service.get_by_strava_id(1234)

    store.get.assert_called_once_with("user:1234", index=None)
    assert result == User(
        strava_id=1234,
        slack_id="slack",
        strava_access_token=UserAccessToken(
            token="another-token",
            expires_at=767676,
            refresh_token="another-refresh-token",
        ),
    )


def test_get_by_strava_id_returns_none_if_no_user_returned(user_service, store):
    store.get.return_value = None
    assert user_service.get_by_strava_id(1234) is None


def test_get_by_slack_id_returns_expected_user_from_db(user_service, store):
    store.get.return_value = {
        "strava_id": 1234,
        "slack_id": "slack",
        "strava_access_token": {
            "token": "another-token",
            "expires_at": 767676,
            "refresh_token": "another-refresh-token",
        },
    }
    result = user_service.get_by_slack_id("slack")

    store.get.assert_called_once_with("slack", index=KeyValueStoreIndex.SLACK_ID)
    assert result == User(
        strava_id=1234,
        slack_id="slack",
        strava_access_token=UserAccessToken(
            token="another-token",
            expires_at=767676,
            refresh_token="another-refresh-token",
        ),
    )


def test_get_by_slack_id_returns_none_if_no_user_returned(user_service, store):
    store.get.return_value = None
    assert user_service.get_by_slack_id("something") is None
