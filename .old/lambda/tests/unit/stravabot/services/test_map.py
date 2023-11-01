from hashlib import sha224
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from stravabot.models import Location, StravaActivity, StravaActivityType
from stravabot.services.map import MapService, activity_as_overlay


@pytest.fixture
def bucket(mocker):
    return mocker.Mock()


@pytest.fixture
def maps(bucket):
    return MapService(bucket)


@patch("stravabot.services.map.polyline")
def test_activity_as_overlay(polyline):
    polyline.decode.return_value = [
        (10, 11),
        (12, 13),
        (14, 15),
    ]

    result = activity_as_overlay(
        StravaActivity(
            activity_id=1,
            name="",
            description="",
            distance=1,
            moving_time=1,
            elapsed_time=1,
            average_speed=1,
            polyline="the-polyline",
            activity_type=StravaActivityType.Run,
            start_location=Location(1, 2),
        )
    )

    polyline.decode.assert_called_once_with("the-polyline")
    assert result == "pin-l-s+2CB5F2(11,10),pin-l-e+2CB5F2(15,14),path-3+2CB5F2-1(the-polyline)"


@patch("stravabot.services.map.mapbox")
@patch("stravabot.services.map.activity_as_overlay")
def test_generate_map_sends_expected_overlay_to_mapbox(activity_as_overlay, mapbox, maps, bucket, mocker):
    bucket.Object.return_value.load.side_effect = ClientError({"Error": {"Code": "404"}}, "")
    activity_as_overlay.return_value = "the-overlay"
    activity = mocker.Mock()

    maps.generate_map(activity)

    activity_as_overlay.assert_called_once_with(activity)
    mapbox.static_image.assert_called_once_with("the-overlay")


@patch("stravabot.services.map.CDN_HOST", "https://the-cdn-host")
@patch("stravabot.services.map.activity_as_overlay", return_value="the-overlay")
@patch("stravabot.services.map.mapbox")
def test_generate_map_returns_expected_url(mapbox, activity_as_overlay, maps, bucket, mocker):
    bucket.Object.return_value.load.side_effect = ClientError({"Error": {"Code": "404"}}, "")
    activity = mocker.Mock()

    url = maps.generate_map(activity)

    assert url == f"https://the-cdn-host/routes/{sha224(b'the-overlay').hexdigest()}.png"


@patch("stravabot.services.map.CDN_HOST", "https://the-cdn-host")
@patch("stravabot.services.map.activity_as_overlay", return_value="the-overlay")
@patch("stravabot.services.map.mapbox")
def test_generate_map_checks_if_object_already_exists(mapbox, activity_as_overlay, maps, bucket, mocker):
    activity = mocker.Mock()

    url = maps.generate_map(activity)

    bucket.Object.assert_called_once_with(f"routes/{sha224(b'the-overlay').hexdigest()}.png")
    bucket.Object.return_value.load.assert_called_once()
    mapbox.static_image.assert_not_called()
    bucket.upload_fileobj.assert_not_called()
    assert url == f"https://the-cdn-host/routes/{sha224(b'the-overlay').hexdigest()}.png"


@patch("stravabot.services.map.CDN_HOST", "https://the-cdn-host")
@patch("stravabot.services.map.activity_as_overlay", return_value="the-overlay")
@patch("stravabot.services.map.mapbox")
def test_generate_map_saves_map_if_not_already_exists(mapbox, activity_as_overlay, maps, bucket, mocker):
    bucket.Object.return_value.load.side_effect = ClientError({"Error": {"Code": "404"}}, "")
    activity = mocker.Mock()

    url = maps.generate_map(activity)

    bucket.upload_fileobj.assert_called_once_with(
        mapbox.static_image.return_value,
        f"routes/{sha224(b'the-overlay').hexdigest()}.png",
        ExtraArgs={"ContentType": "image/png"},
    )
    assert url == f"https://the-cdn-host/routes/{sha224(b'the-overlay').hexdigest()}.png"
