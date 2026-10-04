"""Command-line interface for walltime-lab."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import timedelta
from importlib.metadata import PackageNotFoundError, version

from walltime_lab import __version__
from walltime_lab.transitions import find_transitions


def _installed_version() -> str:
    """Return the installed package version, including source-tree use."""
    try:
        return version("walltime-lab")
    except PackageNotFoundError:
        return __version__


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="walltime-lab",
        description=(
            "Find local clock gaps and overlaps caused by IANA time-zone "
            "offset changes."
        ),
        epilog=(
            "The result uses the time-zone database installed on this system. "
            "Rules can change when governments update civil-time law."
        ),
    )
    parser.add_argument("time_zone", help="IANA zone, for example Europe/Amsterdam")
    parser.add_argument("year", type=int, help="calendar year (1970–9998)")
    parser.add_argument(
        "--json",
        action="store_true",
        help="write machine-readable JSON",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_installed_version()}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return its process exit code."""
    parser = build_parser()
    arguments = parser.parse_args(argv)

    try:
        transitions = find_transitions(arguments.time_zone, arguments.year)
    except (TypeError, ValueError) as error:
        parser.error(str(error))

    if arguments.json:
        payload = {
            "zone": arguments.time_zone,
            "year": arguments.year,
            "transitions": [item.to_dict() for item in transitions],
        }
        print(json.dumps(payload, indent=2))
        return 0

    if not transitions:
        print(f"No offset changes found for {arguments.time_zone} in {arguments.year}.")
        return 0

    print(f"{arguments.time_zone} — local clock changes in {arguments.year}")
    for transition in transitions:
        local_start, local_end = transition.affected_local_interval
        effect = "skipped" if transition.kind == "gap" else "repeated"
        print(
            f"{transition.at_utc:%Y-%m-%d %H:%M:%S} UTC | "
            f"{_format_offset(transition.offset_before)} → "
            f"{_format_offset(transition.offset_after)} | "
            f"{effect} {local_start:%Y-%m-%d %H:%M:%S}–"
            f"{local_end:%Y-%m-%d %H:%M:%S} local"
        )
    return 0


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


if __name__ == "__main__":
    sys.exit(main())
