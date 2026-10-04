"""Tests for transition detection and result semantics."""

from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from walltime_lab import Transition, find_transitions
from walltime_lab.transitions import _find_offset_changes


class TransitionTests(unittest.TestCase):
    def test_finds_forward_and_backward_changes_to_second_precision(self) -> None:
        spring = datetime(2026, 3, 29, 1, 17, 23, tzinfo=UTC)
        autumn = datetime(2026, 10, 25, 1, 42, 11, tzinfo=UTC)

        def offset_at(instant: datetime) -> timedelta:
            if instant < spring:
                return timedelta(0)
            if instant < autumn:
                return timedelta(hours=1)
            return timedelta(0)

        changes = _find_offset_changes(
            offset_at,
            datetime(2026, 1, 1, tzinfo=UTC),
            datetime(2027, 1, 1, tzinfo=UTC),
            scan_step=timedelta(hours=6),
        )

        self.assertEqual(
            changes,
            [
                (spring, timedelta(0), timedelta(hours=1)),
                (autumn, timedelta(hours=1), timedelta(0)),
            ],
        )

    def test_finds_real_iana_gaps_and_overlaps(self) -> None:
        transitions = find_transitions("Europe/Amsterdam", 2024)

        self.assertEqual(len(transitions), 2)
        spring, autumn = transitions
        self.assertEqual(spring.kind, "gap")
        self.assertEqual(spring.at_utc, datetime(2024, 3, 31, 1, tzinfo=UTC))
        self.assertEqual(
            spring.affected_local_interval,
            (
                datetime(2024, 3, 31, 2),
                datetime(2024, 3, 31, 3),
            ),
        )
        self.assertEqual(autumn.kind, "overlap")
        self.assertEqual(autumn.at_utc, datetime(2024, 10, 27, 1, tzinfo=UTC))
        self.assertEqual(
            autumn.affected_local_interval,
            (
                datetime(2024, 10, 27, 2),
                datetime(2024, 10, 27, 3),
            ),
        )

    def test_fixed_offset_zone_has_no_changes(self) -> None:
        transitions = find_transitions("Etc/GMT-3", 2026)
        self.assertEqual(transitions, [])

    def test_transition_json_uses_explicit_local_interval(self) -> None:
        transition = Transition(
            zone="Europe/Amsterdam",
            at_utc=datetime(2024, 3, 31, 1, tzinfo=UTC),
            offset_before=timedelta(hours=1),
            offset_after=timedelta(hours=2),
            before_local=datetime(2024, 3, 31, 2),
            after_local=datetime(2024, 3, 31, 3),
        )

        result = transition.to_dict()

        self.assertEqual(result["kind"], "gap")
        self.assertEqual(result["at_utc"], "2024-03-31T01:00:00Z")
        self.assertEqual(result["offset_before"], "+01:00")
        self.assertEqual(result["offset_after"], "+02:00")
        self.assertEqual(result["local_start"], "2024-03-31 02:00:00")
        self.assertEqual(result["local_end"], "2024-03-31 03:00:00")
        self.assertEqual(result["offset_change_seconds"], 3600)

    def test_seconds_in_utc_offset_are_preserved(self) -> None:
        transition = Transition(
            zone="Test/Seconds",
            at_utc=datetime(2026, 1, 1, tzinfo=UTC),
            offset_before=timedelta(seconds=30),
            offset_after=timedelta(seconds=60),
            before_local=datetime(2026, 1, 1, 0, 0, 30),
            after_local=datetime(2026, 1, 1, 0, 1),
        )
        self.assertEqual(transition.to_dict()["offset_before"], "+00:00:30")
        self.assertEqual(transition.to_dict()["offset_after"], "+00:01")

    def test_rejects_unknown_zone_and_invalid_years(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown IANA time zone"):
            find_transitions("Mars/Olympus", 2026)
        with self.assertRaisesRegex(ValueError, "between 1970 and 9998"):
            find_transitions("UTC", 1969)
        with self.assertRaises(TypeError):
            find_transitions("UTC", True)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            find_transitions(1, 2026)  # type: ignore[arg-type]

    def test_transition_rejects_invalid_datetime_semantics(self) -> None:
        with self.assertRaisesRegex(ValueError, "at_utc must be timezone-aware"):
            Transition(
                zone="UTC",
                at_utc=datetime(2026, 1, 1),
                offset_before=timedelta(0),
                offset_after=timedelta(hours=1),
                before_local=datetime(2026, 1, 1),
                after_local=datetime(2026, 1, 1, 1),
            )
        with self.assertRaisesRegex(ValueError, "must be naive"):
            Transition(
                zone="UTC",
                at_utc=datetime(2026, 1, 1, tzinfo=UTC),
                offset_before=timedelta(0),
                offset_after=timedelta(hours=1),
                before_local=datetime(2026, 1, 1, tzinfo=UTC),
                after_local=datetime(2026, 1, 1, 1),
            )
        with self.assertRaisesRegex(ValueError, "must change"):
            Transition(
                zone="UTC",
                at_utc=datetime(2026, 1, 1, tzinfo=UTC),
                offset_before=timedelta(0),
                offset_after=timedelta(0),
                before_local=datetime(2026, 1, 1),
                after_local=datetime(2026, 1, 1, 1),
            )

    def test_finds_no_changes_for_utc(self) -> None:
        self.assertEqual(find_transitions("UTC", 2026), [])

    def test_invalid_scan_step_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            _find_offset_changes(
                lambda instant: timedelta(0),
                datetime(2026, 1, 1, tzinfo=UTC),
                datetime(2026, 1, 2, tzinfo=UTC),
                scan_step=timedelta(0),
            )

    def test_naive_scan_bounds_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            _find_offset_changes(
                lambda instant: timedelta(0),
                datetime(2026, 1, 1),
                datetime(2026, 1, 2, tzinfo=UTC),
            )

    def test_empty_scan_interval_is_empty(self) -> None:
        bound = datetime(2026, 1, 1, tzinfo=UTC)
        self.assertEqual(
            _find_offset_changes(lambda instant: timedelta(0), bound, bound),
            [],
        )


if __name__ == "__main__":
    unittest.main()
