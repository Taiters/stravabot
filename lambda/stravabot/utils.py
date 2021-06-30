from datetime import datetime, timedelta


def ttl_to_unixtime(ttl: timedelta) -> int:
    time = datetime.utcnow() + ttl
    return round(time.timestamp())
