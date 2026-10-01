"""All date logic goes through here so "today" is always the school's today
(America/New_York by default), never the server clock's timezone."""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from backend import config


def tz() -> ZoneInfo:
    return ZoneInfo(config.APP_TZ)


def now_local() -> datetime:
    return datetime.now(tz())


def today() -> date:
    return now_local().date()


def to_local(utc_naive: datetime) -> datetime:
    return utc_naive.replace(tzinfo=timezone.utc).astimezone(tz())


def local_to_utc_naive(local: datetime) -> datetime:
    return local.astimezone(timezone.utc).replace(tzinfo=None)


def next_business_day(d: date) -> date:
    nxt = d + timedelta(days=1)
    while nxt.weekday() >= 5:  # Saturday=5, Sunday=6
        nxt += timedelta(days=1)
    return nxt


def fmt_day(d: date) -> str:
    """'Friday, Oct 9' — dates in words for people and the assistant."""
    return f"{d.strftime('%A')}, {d.strftime('%b')} {d.day}"


def fmt_short_day(d: date) -> str:
    return f"{d.strftime('%a')}, {d.strftime('%b')} {d.day}"


def fmt_datetime(utc_naive: datetime) -> str:
    local = to_local(utc_naive)
    hour = local.strftime("%I").lstrip("0")
    return f"{local.strftime('%b')} {local.day}, {hour}:{local.strftime('%M %p')}"


def ago(utc_naive: datetime) -> str:
    delta = now_local() - to_local(utc_naive)
    minutes = int(delta.total_seconds() // 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} h ago"
    days = hours // 24
    return "yesterday" if days == 1 else f"{days} days ago"
