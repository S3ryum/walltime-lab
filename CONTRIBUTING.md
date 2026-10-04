# Contributing

Thanks for considering a contribution.

## Setup

Use Python 3.11 or newer. Run make setup to create a virtual environment, install pinned development tools, and install the package in editable mode.

## Before opening a pull request

- Keep runtime dependencies at zero unless a feature requires one.
- Add deterministic tests for behavior changes. Do not rely on the network or current date.
- Run make check and include the relevant output in the pull request description.
- Update documentation and CHANGELOG.md when user-visible behavior changes.
- Use a Conventional Commit subject, such as fix: preserve non-hour offsets.

## Reporting issues

Use the bug or feature issue template. Include the Python version, operating system, IANA zone, year, and the installed tzdata source/version when relevant. Avoid including private calendar data.
