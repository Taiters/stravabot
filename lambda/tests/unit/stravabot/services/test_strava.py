from unittest.mock import patch
from urllib.parse import urlencode

from stravabot.services import strava


@patch("stravabot.services.strava.STRAVA_CLIENT_ID", "strava-client-id")
@patch("stravabot.services.strava.STRAVA_CALLBACK_URL", "http://the-callback-url/test")
def test_get_oauth_url_returns_expected_url():
    result = strava.get_oauth_url("a-token")
    expected_params = urlencode(
        {
            "client_id": "strava-client-id",
            "redirect_uri": "http://the-callback-url/test?token=a-token",
            "response_type": "code",
            "scope": "read,activity:read",
        }
    )
    assert result == f"https://www.strava.com/oauth/authorize?{expected_params}"


@patch("stravabot.services.strava.STRAVA_CLIENT_ID", "strava-client-id")
@patch("stravabot.services.strava.STRAVA_CLIENT_SECRET", "shh-its-a-secret")
def test_get_athlete_credentials_returns_expected_credentials(requests_mock):
    requests_mock.post(
        "https://www.strava.com/api/v3/oauth/token",
        json={
            "athlete": {"id": "athlete-id"},
            "access_token": "the-access-token",
            "refresh_token": "the-refresh-token",
            "expires_at": 123456,
        },
    )
    result = strava.get_athlete_credentials("a-code")

    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == {
        "client_id": "strava-client-id",
        "client_secret": "shh-its-a-secret",
        "code": "a-code",
        "grant_type": "authorization_code",
    }
    assert result == strava.StravaAthleteCredentials(
        id="athlete-id",
        access_token="the-access-token",
        refresh_token="the-refresh-token",
        expires_at=123456,
    )
