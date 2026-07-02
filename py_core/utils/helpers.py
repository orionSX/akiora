from datetime import datetime, UTC


def time_now():
    return datetime.now(tz=UTC)
