PYTHON ?= python3
VENV = .venv
BIN = $(VENV)/bin/

.PHONY: setup dev test lint type-check audit build check clean

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)pip install -r requirements-dev.lock
	$(BIN)pip install --no-build-isolation -e .

dev:
	$(BIN)walltime-lab Europe/Amsterdam 2026

test:
	$(BIN)coverage erase
	$(BIN)coverage run -m unittest discover -s tests -v
	$(BIN)coverage report --fail-under=80

lint:
	$(BIN)ruff check src tests
	$(BIN)ruff format --check src tests

type-check:
	$(BIN)mypy --strict src/walltime_lab

audit:
	$(BIN)pip-audit -r requirements-dev.lock

build:
	$(BIN)python -m build

check: lint type-check test audit build

clean:
	rm -rf .venv .coverage build dist src/*.egg-info
