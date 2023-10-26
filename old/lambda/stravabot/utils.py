from datetime import datetime, timedelta


def ttl_to_unixtime(ttl: timedelta) -> int:
    time = datetime.utcnow() + ttl
    return round(time.timestamp())


def format_time(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"
