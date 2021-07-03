from datetime import datetime, timedelta

from stravabot.utils import ttl_to_unixtime


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
