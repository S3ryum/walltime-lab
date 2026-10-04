# Research notes

**Date:** 2026-10-04 (Europe/Istanbul)  
**Category:** Reusable Python library, selected as the least represented recent project category from the account repository list and descriptions. A daily-journal history was absent at the start.

## Questions and findings

- **Where do civil-time rules come from?** The IANA Time Zone Database records location-based clock changes and is updated when governments change rules. Release 2026b (2026-04-22) moved British Columbia to permanent UTC−07. This supports reading installed rules instead of hard-coding seasonal behavior. IANA also cautions that pre-1970 history is incomplete and future rules can change.
- **Can Python read these rules without a runtime dependency?** Python 3.14 zoneinfo reads system data and falls back to the first-party tzdata PyPI package. Windows installations may lack system data, so tzdata is optional. No required network service is used.
- **What makes wall-clock readings tricky?** A forward offset change creates readings that never occur; a backward change repeats a local interval. Some political offset changes are not DST, so results describe direction and gap/overlap rather than assuming a DST label.
- **Do developers report related failures?** Issues in date-fns-tz, n8n, and Microsoft Work IQ describe confusing offsets, recurring meeting shifts, and missing zone labels. They support output that distinguishes UTC instants from local wall time.
- **What exists already?** GitHub timezone and world-clock topics contain converters, clocks, and meeting planners. gy-vs/tz-local-gap-web is an adjacent timezone-data workbench; its README describes timezone bundles, not a Python API for enumerating skipped/repeated intervals. The selected scope focuses on that diagnostic job and reusable output.
- **What did I select?** Python ZoneInfo is standard library since Python 3.9. This package supports Python 3.11+, has no required runtime dependency, and offers an optional tzdata extra. PyPI versions checked 2026-10-04: setuptools 84.0.0, build 1.6.1, coverage 7.16.2, Ruff 0.16.10, mypy 2.4.0, pip-audit 2.10.1, tzdata 2026.5. GitHub Actions checkout and setup-python v7 tags were resolved to commit SHAs in CI.

## Decision and learning applied

The algorithm samples UTC offsets every 30 minutes, then binary-searches a detected boundary to the nearest second. I learned to model a transition as a unique UTC instant plus two local wall-clock endpoints: forward changes create a skipped half-open interval, backward changes create a repeated interval. The API applies this in the affected_local_interval property; tests cover synthetic second-level boundaries and Europe/Amsterdam in 2024.

**Limit:** more than one offset change inside a 30-minute interval may be missed or collapsed into one result. Results follow the host's installed tzdata and can change after updates.

## Idea selection

Scores are 1–5 for usefulness, originality, demo value, finishability, testability, and maintenance (30 max).

| Candidate | U | O | Demo | Finish | Test | Maintain | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Walltime transition API + CLI | 5 | 4 | 5 | 5 | 5 | 5 | 29 |
| Local gap/overlap playground | 5 | 4 | 5 | 4 | 5 | 4 | 27 |
| Time-zone database release diff | 4 | 5 | 4 | 3 | 4 | 3 | 23 |
| Cron preview by zone | 4 | 3 | 5 | 4 | 4 | 4 | 24 |
| Recurring-event DST checker | 5 | 3 | 4 | 4 | 4 | 3 | 23 |
| TZif header inspector | 3 | 4 | 3 | 4 | 5 | 5 | 24 |
| Time-zone abbreviation linter | 3 | 3 | 3 | 5 | 5 | 5 | 24 |
| Leap-second timeline lesson | 3 | 4 | 5 | 4 | 3 | 4 | 23 |
| Team overlap calendar | 4 | 2 | 3 | 4 | 4 | 3 | 20 |
| UTC offset comparison matrix | 3 | 2 | 3 | 5 | 5 | 5 | 23 |

## Sources

1. IANA, Time Zone Database Release 2026b: https://www.iana.org/time-zones/releases/2026b
2. IANA, theory and limitations: https://www.iana.org/time-zones/theory
3. Python 3.14 zoneinfo documentation: https://docs.python.org/3.14/library/zoneinfo.html
4. IETF RFC 9636, TZif format: https://www.rfc-editor.org/rfc/rfc9636.html
5. MDN, Temporal.ZonedDateTime gaps and ambiguities: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal/ZonedDateTime
6. date-fns-tz issue 227: https://github.com/marnusw/date-fns-tz/issues/227
7. n8n issue 11264: https://github.com/n8n-io/n8n/issues/11264
8. Microsoft Work IQ issue 160: https://github.com/microsoft/work-iq/issues/160
9. GitHub timezone-converter topic: https://github.com/topics/timezone-converter
10. GitHub world-clock topic: https://github.com/topics/world-clock
11. Adjacent project README: https://github.com/gy-vs/tz-local-gap-web
12. PyPI version records: https://pypi.org/project/setuptools/ ; https://pypi.org/project/build/ ; https://pypi.org/project/coverage/ ; https://pypi.org/project/ruff/ ; https://pypi.org/project/mypy/ ; https://pypi.org/project/pip-audit/ ; https://pypi.org/project/tzdata/
13. GitHub Actions release sources: https://github.com/actions/checkout/releases ; https://github.com/actions/setup-python/releases
