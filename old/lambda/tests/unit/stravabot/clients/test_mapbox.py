from unittest.mock import patch

import pytest
from urllib3.response import HTTPResponse

from stravabot.clients import mapbox


@patch("stravabot.clients.mapbox.MAPBOX_ACCESS_TOKEN", "mapbox-access-token")
def test_static_image(requests_mock):
    expected_response = HTTPResponse(body="the-raw-response", status=200)
    requests_mock.get(
        "https://api.mapbox.com/styles/v1/mapbox/light-v10/static/the-overlay/auto/123x456",
        raw=expected_response,
    )
    response = mapbox.static_image("the-overlay", 123, 456)

    assert requests_mock.call_count == 1
    assert requests_mock.last_request.qs == {"access_token": ["mapbox-access-token"]}
    assert response == expected_response


@patch("stravabot.clients.mapbox.MAPBOX_ACCESS_TOKEN", "mapbox-access-token")
def test_static_image_raises_on_non_200(requests_mock):
    expected_response = HTTPResponse(body="the-raw-response", status=500)
    requests_mock.get(
        "https://api.mapbox.com/styles/v1/mapbox/light-v10/static/the-overlay/auto/123x456",
        raw=expected_response,
    )
    with pytest.raises(mapbox.MapboxError):
        mapbox.static_image("the-overlay", 123, 456)
