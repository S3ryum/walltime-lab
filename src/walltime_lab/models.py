"""Immutable transition result types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal


@dataclass(frozen=True, slots=True)
class Transition:
    """One IANA offset change and its affected local wall-time interval.

    The local datetimes are naive by design: they are wall-clock readings in
    the named zone, not UTC instants. Use at_utc for the unique transition
    instant.
    """

    zone: str
    at_utc: datetime
    offset_before: timedelta
    offset_after: timedelta
    before_local: datetime
    after_local: datetime

    def __post_init__(self) -> None:
        if self.at_utc.tzinfo is None or self.at_utc.utcoffset() is None:
            raise ValueError("at_utc must be timezone-aware")
        if self.before_local.tzinfo is not None or self.after_local.tzinfo is not None:
            raise ValueError("local wall-clock endpoints must be naive")
        if self.offset_before == self.offset_after:
            raise ValueError("a transition must change the UTC offset")

    @property
    def direction(self) -> Literal["forward", "backward"]:
        """Return whether the local clock moves forward or backward."""
        return "forward" if self.offset_after > self.offset_before else "backward"

    @property
    def kind(self) -> Literal["gap", "overlap"]:
        """Return gap for skipped local time or overlap for repeated local time."""
        return "gap" if self.direction == "forward" else "overlap"

    @property
    def affected_local_interval(self) -> tuple[datetime, datetime]:
        """Return the half-open naive wall-time interval that changes meaning."""
        if self.direction == "forward":
            return self.before_local, self.after_local
        return self.after_local, self.before_local

    def to_dict(self) -> dict[str, str | int]:
        """Return a JSON-ready representation with explicit UTC and local fields."""
        local_start, local_end = self.affected_local_interval
        return {
            "zone": self.zone,
            "kind": self.kind,
            "direction": self.direction,
            "at_utc": _iso_utc(self.at_utc),
            "offset_before": _format_offset(self.offset_before),
            "offset_after": _format_offset(self.offset_after),
            "offset_change_seconds": int(
                (self.offset_after - self.offset_before).total_seconds()
            ),
            "local_start": local_start.isoformat(sep=" ", timespec="seconds"),
            "local_end": local_end.isoformat(sep=" ", timespec="seconds"),
        }


def _iso_utc(value: datetime) -> str:
    """Format an aware datetime as an ISO-8601 UTC timestamp."""
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _format_offset(value: timedelta) -> str:
    """Format an offset with seconds when the database includes them."""
    total_seconds = int(value.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    absolute_seconds = abs(total_seconds)
    hours, remainder = divmod(absolute_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if seconds:
        return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{sign}{hours:02d}:{minutes:02d}"
