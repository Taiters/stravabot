from datetime import datetime, timedelta

from stravabot.utils import seconds_to_minutes, ttl_to_unixtime


def test_ttl_to_unixtime_returns_expcted_timestamp(freezer):
    freezer.move_to("2021-01-01T00:00:00")
    result = ttl_to_unixtime(timedelta(hours=1, minutes=23, seconds=45))
    assert datetime.fromtimestamp(result) == datetime(
        year=2021,
        month=1,
        day=1,
        hour=1,
        minute=23,
        second=45,
    )


def test_seconds_to_minutes():
    assert seconds_to_minutes(1234) == "20:34"


def test_seconds_to_minutes_with_float():
    assert seconds_to_minutes(5678.123) == "94:38"  # type: ignore
