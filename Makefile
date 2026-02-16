CONFIG ?= monitor.json.example
DEBUG_FLAG := $(if $(DEBUG),--debug,)
VENV := venv/bin

.PHONY: cli monitor test format

cli:
	$(VENV)/python -m pryces.presentation.console.cli $(DEBUG_FLAG)

monitor:
	$(VENV)/python -m pryces.presentation.scripts.monitor_stocks $(CONFIG) $(DEBUG_FLAG)

test:
	$(VENV)/pytest

format:
	$(VENV)/black src/ tests/ --line-length 100
