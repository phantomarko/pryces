CONFIG ?= monitor.json.example
DEBUG_FLAG := $(if $(DEBUG),--debug,)

.PHONY: venv cli monitor test format

venv:
	@echo "Run: source venv/bin/activate"

cli:
	python -m pryces.presentation.console.cli $(DEBUG_FLAG)

monitor:
	python -m pryces.presentation.scripts.monitor_stocks $(CONFIG) $(DEBUG_FLAG)

test:
	pytest

format:
	black src/ tests/ --line-length 100
