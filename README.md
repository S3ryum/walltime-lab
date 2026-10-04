# walltime-lab

Find the local clock interval that disappears or repeats when an IANA time-zone offset changes. [Türkçe özet](README.tr.md)

## Why?

Time-zone converters answer “what time is it there?” Walltime-lab answers a different debugging question: “which local readings are missing or duplicated in this zone and year?” It is a small reusable Python API and CLI, with no required runtime dependencies and no network calls.

The output reports actual offset changes from the installed IANA database, including non-hour changes, without assuming that every change is daylight-saving time.

## Demo

Run:

~~~console
$ walltime-lab Europe/Amsterdam 2026
Europe/Amsterdam — local clock changes in 2026
2026-03-29 01:00:00 UTC | +01:00 → +02:00 | skipped 2026-03-29 02:00:00–2026-03-29 03:00:00 local
2026-10-25 01:00:00 UTC | +02:00 → +01:00 | repeated 2026-10-25 02:00:00–2026-10-25 03:00:00 local
~~~

This is real CLI output captured with the host’s installed time-zone database.

## Features

- Find transitions for any installed IANA time zone from 1970 onward.
- Distinguish skipped wall times (gaps) from repeated wall times (overlaps).
- Preserve second-level offsets and transition instants.
- Return immutable Python objects or JSON.
- Work offline using the system database; install the optional tzdata extra on systems without IANA data, including many Windows setups.

## Quick start

~~~sh
python -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/walltime-lab Europe/Amsterdam 2026
~~~

On Windows, install the optional database fallback with this command: python -m pip install ".[tzdata]".

## Usage

~~~sh
walltime-lab Europe/Amsterdam 2026
walltime-lab America/New_York 2026 --json
walltime-lab UTC 2026
~~~

The JSON form includes the UTC transition instant, offsets before and after, change direction, and local interval endpoints. Unknown zones and unsupported years exit with status 2 and a concise message. Help, version, and JSON output are supported. Output is plain text and respects NO_COLOR because it emits no terminal color codes.

### Python API

~~~python
from walltime_lab import find_transitions

for change in find_transitions("Europe/Amsterdam", 2026):
    start, end = change.affected_local_interval
    print(change.kind, start, end, change.at_utc)
~~~

find_transitions(time_zone, year) returns ordered Transition objects. Local interval endpoints are naive wall-clock values; at_utc is an aware UTC instant. See [API docs](docs/API.md), [design](docs/DESIGN.md), and [research](docs/RESEARCH.md).

## How it works

Walltime-lab checks UTC instants against Python’s zoneinfo offsets at 30-minute intervals. When an offset differs, it binary-searches the boundary to the nearest second. A forward jump creates a gap; a backward jump creates an overlap.

## Options

| Input | Meaning |
| --- | --- |
| time_zone | IANA zone identifier such as Europe/Amsterdam |
| year | Gregorian year from 1970 through 9998 |
| --json | Emit machine-readable JSON |
| --version | Print installed version |
| --help | Show command help |

## Development

Run make setup once, then:

~~~sh
make test
make lint
make type-check
make audit
make build
make check
~~~

make check runs lint, formatting, strict type-checking, tests with coverage, dependency audit, and wheel/sdist build. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Limitations

Results follow the time-zone database installed on the host and may differ after that database is updated. IANA documents incomplete pre-1970 history and future rule changes. Queries are limited to 1970–9998. The scan assumes at most one offset change per 30-minute interval; multiple changes may be missed or collapsed into one result. The library reports offset changes; it does not decide how an application should resolve an ambiguous local datetime.

## Roadmap

- Add a helper to classify one supplied local datetime as unique, missing, or repeated.
- Add an optional machine-readable JSON schema.
- Expand test cases for political offset changes that are not seasonal DST.

## References

- [IANA Time Zone Database](https://www.iana.org/time-zones) and [database limitations](https://www.iana.org/time-zones/theory)
- [Python zoneinfo documentation](https://docs.python.org/3.14/library/zoneinfo.html)
- [RFC 9636: TZif](https://www.rfc-editor.org/rfc/rfc9636.html)
- [Real DST offset issue in date-fns-tz](https://github.com/marnusw/date-fns-tz/issues/227)

## Contributing and license

Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). Released under the MIT License.
