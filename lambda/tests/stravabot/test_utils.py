from datetime import timedelta, datetime

from stravabot.utils import ttl_to_unixtime


def test_utils(freezer):
    freezer.move_to("2021-01-01T00:00:00")
    result = ttl_to_unixtime(timedelta(hours=1, minutes=23, seconds=45))
    assert datetime.fromtimestamp(result) == datetime(
        year=2021,
        month=1,
        day=1,
        hour=1,
        minute=2,
        second=45,
    )