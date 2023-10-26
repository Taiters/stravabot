from datetime import datetime, timedelta

from stravabot.utils import format_time, ttl_to_unixtime


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


def test_format_time():
    assert format_time(1234) == "20:34"


def test_format_time_with_float():
    assert format_time(1234.123) == "20:34"  # type: ignore


def test_format_time_with_hours():
    assert format_time(5678) == "01:34:38"


def test_format_time_with_padding():
    assert format_time(3723) == "01:02:03"
