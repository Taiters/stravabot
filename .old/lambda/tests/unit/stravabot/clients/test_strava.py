from unittest.mock import patch
from urllib.parse import urlencode

from stravabot.clients import strava


@patch("stravabot.clients.strava.STRAVA_CLIENT_ID", "strava-client-id")
@patch("stravabot.clients.strava.HOST", "http://the-host")
def test_oauth_url_returns_expected_url():
    result = strava.oauth_url("a-token")
    expected_params = urlencode(
        {
            "client_id": "strava-client-id",
            "redirect_uri": "http://the-host/strava/auth?token=a-token",
            "response_type": "code",
            "scope": "read,activity:read",
        }
    )
    assert result == f"https://www.strava.com/oauth/authorize?{expected_params}"


@patch("stravabot.clients.strava.STRAVA_CLIENT_ID", "strava-client-id")
@patch("stravabot.clients.strava.STRAVA_CLIENT_SECRET", "shh-its-a-secret")
def test_oauth_token_with_code_makes_expected_call(requests_mock):
    requests_mock.post("https://www.strava.com/api/v3/oauth/token", json={"foo": "bar"})
    result = strava.oauth_token(code="a-code")

    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == {
        "client_id": "strava-client-id",
        "client_secret": "shh-its-a-secret",
        "code": "a-code",
        "grant_type": "authorization_code",
    }
    assert result == {"foo": "bar"}


@patch("stravabot.clients.strava.STRAVA_CLIENT_ID", "strava-client-id")
@patch("stravabot.clients.strava.STRAVA_CLIENT_SECRET", "shh-its-a-secret")
def test_oauth_token_with_refresh_token_makes_expected_call(requests_mock):
    requests_mock.post("https://www.strava.com/api/v3/oauth/token", json={"foo": "bar"})
    result = strava.oauth_token(refresh_token="a-refresh-token")

    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == {
        "client_id": "strava-client-id",
        "client_secret": "shh-its-a-secret",
        "refresh_token": "a-refresh-token",
        "grant_type": "refresh_token",
    }
    assert result == {"foo": "bar"}
