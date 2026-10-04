# API

## find_transitions(time_zone, year)

Returns an ordered list of immutable Transition values.

- time_zone: an installed IANA identifier, for example Europe/Amsterdam.
- year: integer from 1970 through 9998.
- Raises TypeError for wrong argument types and ValueError for an unknown zone or unsupported year.

Each result contains:

- at_utc: aware UTC datetime for the unique instant of change.
- offset_before, offset_after: UTC offsets as timedeltas.
- before_local, after_local: naive local wall-clock readings on either side.
- direction: forward or backward.
- kind: gap or overlap.
- affected_local_interval: half-open naive interval of missing or repeated readings.
- to_dict(): JSON-ready mapping with explicit offset and interval fields.

Example:

~~~python
from walltime_lab import find_transitions

changes = find_transitions("Europe/Amsterdam", 2026)
for change in changes:
    start, end = change.affected_local_interval
    print(f"{change.kind}: {start} to {end}; UTC boundary {change.at_utc}")
~~~

Walltime-lab reports offset transitions from the installed database. It does not resolve a local datetime into a UTC instant.
