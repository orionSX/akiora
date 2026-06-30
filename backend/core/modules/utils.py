from datetime import datetime, UTC


def time_now():
    return datetime.now(tz=UTC)


def default_name():
    return f"user{int(time_now().timestamp())}"
