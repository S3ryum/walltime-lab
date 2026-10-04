"""Discover clock transitions from the host's IANA time-zone database."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from walltime_lab.models import Transition

_SCAN_STEP = timedelta(minutes=30)
_PADDING = timedelta(days=2)
_MIN_YEAR = 1970
_MAX_YEAR = 9998


def find_transitions(time_zone: str, year: int) -> list[Transition]:
    """Find local-clock gaps and overlaps for an IANA zone in a calendar year.

    The result is derived from the zone data installed with Python or the
    optional tzdata package. It reports offset changes regardless of whether
    local law describes them as daylight saving time.

    Args:
        time_zone: IANA time-zone identifier such as Europe/Amsterdam.
        year: Gregorian year from 1970 through 9998.

    Returns:
        Transitions ordered by their unique UTC instant.

    Raises:
        TypeError: If time_zone or year has the wrong type.
        ValueError: If the zone is unknown or the year is out of range.
    """
    if not isinstance(time_zone, str):
        raise TypeError("time_zone must be a string IANA identifier")
    if isinstance(year, bool) or not isinstance(year, int):
        raise TypeError("year must be an integer")

    if not _MIN_YEAR <= year <= _MAX_YEAR:
        raise ValueError(f"year must be between {_MIN_YEAR} and {_MAX_YEAR}")

    try:
        zone = ZoneInfo(time_zone)
    except (ZoneInfoNotFoundError, ValueError) as error:
        raise ValueError(f"unknown IANA time zone: {time_zone!r}") from error

    start = datetime(year, 1, 1, tzinfo=UTC) - _PADDING
    end = datetime(year + 1, 1, 1, tzinfo=UTC) + _PADDING

    def offset_at(instant: datetime) -> timedelta:
        offset = instant.astimezone(zone).utcoffset()
        if offset is None:
            raise RuntimeError(f"time zone {time_zone!r} returned no UTC offset")
        return offset

    changes = _find_offset_changes(offset_at, start, end)
    results: list[Transition] = []

    for at_utc, offset_before, offset_after in changes:
        before_local = (at_utc + offset_before).replace(tzinfo=None)
        after_local = (at_utc + offset_after).replace(tzinfo=None)
        if before_local.year != year and after_local.year != year:
            continue
        results.append(
            Transition(
                zone=time_zone,
                at_utc=at_utc,
                offset_before=offset_before,
                offset_after=offset_after,
                before_local=before_local,
                after_local=after_local,
            )
        )

    return results


def _find_offset_changes(
    offset_at: Callable[[datetime], timedelta],
    start: datetime,
    end: datetime,
    scan_step: timedelta = _SCAN_STEP,
) -> list[tuple[datetime, timedelta, timedelta]]:
    """Find offset changes in a UTC interval using bounded sampling and bisection.

    A half-hour sample keeps a yearly scan inexpensive. If offsets differ,
    binary search locates one boundary to the nearest second, matching TZif
    transition precision. Multiple changes inside one sample may be missed
    or collapsed into one result.
    """
    if scan_step <= timedelta(0):
        raise ValueError("scan_step must be greater than zero")
    if start.utcoffset() is None or end.utcoffset() is None:
        raise ValueError("start and end must be timezone-aware UTC datetimes")
    if start >= end:
        return []

    changes: list[tuple[datetime, timedelta, timedelta]] = []
    left = start.astimezone(UTC)
    left_offset = offset_at(left)

    while left < end:
        right = min(left + scan_step, end).astimezone(UTC)
        right_offset = offset_at(right)
        if right_offset != left_offset:
            at_utc, offset_after = _locate_change(offset_at, left, right, left_offset)
            changes.append((at_utc, left_offset, offset_after))
        left = right
        left_offset = right_offset

    return changes


def _locate_change(
    offset_at: Callable[[datetime], timedelta],
    left: datetime,
    right: datetime,
    offset_before: timedelta,
) -> tuple[datetime, timedelta]:
    """Locate the first second with a new offset in a bracketed interval."""
    while (right - left) > timedelta(seconds=1):
        span_seconds = int((right - left).total_seconds())
        middle = left + timedelta(seconds=span_seconds // 2)
        if offset_at(middle) == offset_before:
            left = middle
        else:
            right = middle

    return right, offset_at(right)
