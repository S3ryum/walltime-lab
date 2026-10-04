# Design

## Problem and audience

Developers debugging calendars, schedules, logs, and recurring events need to know which local wall-clock interval disappears or occurs twice when a time-zone offset changes. A UTC instant is unique; an unqualified local reading near a transition may map to zero or two instants.

## MVP

1. A documented Python API returns every offset transition for an IANA zone and year.
2. Results distinguish skipped intervals (gaps) from repeated intervals (overlaps), and include the UTC instant, offsets before and after, and local endpoints.
3. A CLI prints a compact human report or JSON. Invalid zones and years fail with actionable messages.

## Out of scope

- Converting arbitrary local datetimes to UTC or deciding which duplicate instant a caller intended.
- Guessing whether an offset change is legally called daylight-saving time.
- Shipping or updating IANA data, network access, GUI, map, or calendar integrations.
- Claims of authoritative results before 1970 or predictions that survive future law changes.

## Architecture and trade-offs

The models module defines immutable Transition values. The transition module reads the host IANA database through Python zoneinfo, samples offsets across a UTC year window, then binary-searches detected changes to one-second precision. The CLI module provides text and JSON output.

A 30-minute scan keeps a yearly search small. It assumes at most one offset change per scan interval; multiple changes may be missed or collapsed into one result. Tests exercise synthetic second-level offsets and a real IANA zone.

The host database avoids a stale bundled copy and runtime network calls. An optional tzdata extra supports systems without system zone data. Queries are limited to 1970–9998 because IANA describes the post-1970 period most consistently and scan padding must fit datetime bounds. UTC instants stay aware; local wall readings are naive to make their meanings explicit.

## Verification strategy

Unit tests cover second-precision boundaries, forward and backward changes, fixed-offset zones, invalid input, year filtering, and JSON fields. CLI smoke tests run a real IANA example. Ruff, mypy, coverage, pip-audit, and wheel/sdist build are local and CI checks.
