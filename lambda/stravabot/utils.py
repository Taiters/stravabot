from datetime import datetime, timedelta
from math import floor


def ttl_to_unixtime(ttl: timedelta) -> int:
    time = datetime.utcnow() + ttl
    return round(time.timestamp())


def seconds_to_minutes(seconds: int) -> str:
    return f"{floor(seconds / 60)}:{floor(seconds % 60)}"
