from datetime import timedelta

import pytest

from stravabot.services.response_url import ResponseUrlService
from stravabot.services.token import Token


@pytest.fixture
def store(mocker):
    return mocker.Mock()


@pytest.fixture
def tokens(mocker):
    return mocker.Mock()


@pytest.fixture
def response_url_service(store, tokens):
    return ResponseUrlService(store, tokens)


def test_generate_token_returns_expected_token(mocker, response_url_service, tokens):
    mocker.patch("stravabot.services.response_url.uuid4", return_value="a-uuid")
    expected_token = Token("a", {}, "token")
    tokens.generate.return_value = expected_token

    token = response_url_service.generate_token(user_id="a-user-id", ttl=timedelta(minutes=5))

    tokens.generate.assert_called_once_with(
        user_id="a-user-id", data={"response_id": "a-uuid"}, ttl=timedelta(minutes=5)
    )

    assert token == expected_token


def test_put_sends_expected_fields_to_store(store, response_url_service):
    token = Token(slack_user_id="a-user-id", data={"response_id": "a-response-id"}, expires=2524608300, token="")

    response_url_service.put(token, "https://the-url/to/send/to")
    store.put.assert_called_once_with(
        key="response_id:a-user-id:a-response-id",
        value={
            "response_url": "https://the-url/to/send/to",
        },
        expires=2524608300,
    )


def test_get_returns_expected_url(store, response_url_service):
    token = Token(slack_user_id="a-user-id", data={"response_id": "a-response-id"}, expires=2524608300, token="")
    store.get.return_value = {"response_url": "https://send-to-here"}

    result = response_url_service.get(token)
    store.get.assert_called_once_with("response_id:a-user-id:a-response-id")
    assert result == "https://send-to-here"


def test_get_returns_none_if_no_url_exists(store, response_url_service):
    token = Token(slack_user_id="a-user-id", data={"response_id": "a-response-id"}, expires=2524608300, token="")
    store.get.return_value = None
    assert response_url_service.get(token) is None
