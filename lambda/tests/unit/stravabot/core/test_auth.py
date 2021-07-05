from datetime import timedelta
from unittest.mock import patch

import pytest

from stravabot.api import ApiRequest, ApiResponse
from stravabot.core.auth import AuthFlow
from stravabot.models import Token, User, UserAccessToken
from stravabot.services.strava import StravaAthleteCredentials


@pytest.fixture
def users(mocker):
    return mocker.Mock()


@pytest.fixture
def tokens(mocker):
    return mocker.Mock()


@pytest.fixture
def response_urls(mocker):
    return mocker.Mock()


@pytest.fixture
def templates(mocker):
    return mocker.Mock()


@pytest.fixture
def auth_flow(templates, users, tokens, response_urls):
    return AuthFlow(templates, users, tokens, response_urls, timedelta(minutes=10))


@patch("stravabot.core.auth.messages")
@patch("stravabot.core.auth.strava")
def test_send_oauth_url(strava, messages, auth_flow, response_urls, mocker):
    ack = mocker.Mock()
    response_urls.generate_token.return_value = Token(
        slack_user_id="",
        data={},
        token="the-token",
    )
    strava.get_oauth_url.return_value = "the-oauth-url"

    auth_flow.send_oauth_url(ack, {"user_id": "the-user"})

    response_urls.generate_token.assert_called_once_with("the-user", timedelta(minutes=10))
    strava.get_oauth_url.assert_called_once_with("the-token")
    messages.connect_response.assert_called_once_with(
        action_id="authenticate_clicked",
        token="the-token",
        oauth_url="the-oauth-url",
    )
    ack.assert_called_once_with(messages.connect_response.return_value)


def test_store_response_url(auth_flow, tokens, response_urls, mocker):
    ack = mocker.Mock()
    body = {"response_url": "the-response-url"}
    action = {"value": "the-token"}

    auth_flow.store_response_url(ack, body, action)

    tokens.decode.assert_called_once_with("the-token")
    response_urls.put.assert_called_once_with(tokens.decode.return_value, "the-response-url")
    ack.assert_called_once()


@patch("stravabot.core.auth.HOST", "the-host")
def test_handle_strava_callback_returns_template(mocker, auth_flow, templates):
    template = mocker.Mock()
    templates.get_template.return_value = template

    response = auth_flow.handle_strava_callback(
        ApiRequest(
            path="",
            method="",
            query_parameters={
                "token": "a-token",
                "code": "a-code",
            },
        )
    )

    template.render.assert_called_once_with(
        host="the-host",
        parameters={
            "error": None,
            "token": "a-token",
            "code": "a-code",
        },
    )
    assert response == ApiResponse(body=template.render.return_value, headers={"Content-Type": "text/html"})


@patch("stravabot.core.auth.messages")
@patch("stravabot.core.auth.strava")
def test_handle_strava_connect_success(strava, messages, requests_mock, auth_flow, tokens, response_urls, users):
    tokens.decode.return_value = Token(
        slack_user_id="the-slack-id",
        data={},
        token="",
    )
    response_urls.get.return_value = "http://the-response-url/"
    strava.get_athlete_credentials.return_value = StravaAthleteCredentials(
        id="the-strava-id",
        access_token="access-token",
        refresh_token="refresh-token",
        expires_at=1234567,
    )
    messages.connect_result.return_value = {"message": "result"}
    requests_mock.post("http://the-response-url/")

    response = auth_flow.handle_strava_connect(
        ApiRequest(path="", method="", path_parameters={}, body='{"token": "the-token", "code": "the-strava-code"}')
    )

    tokens.decode.assert_called_once_with("the-token")
    response_urls.get.assert_called_once_with(tokens.decode.return_value, max_attempts=3)
    strava.get_athlete_credentials.assert_called_once_with("the-strava-code")
    users.put.assert_called_once_with(
        User(
            strava_id="the-strava-id",
            slack_id="the-slack-id",
            strava_access_token=UserAccessToken(
                token="access-token",
                refresh_token="refresh-token",
                expires_at=1234567,
            ),
        )
    )
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == {"message": "result"}
    assert response == ApiResponse.ok()
