CONFIG ?= monitor.json.example

.PHONY: venv cli monitor test format

venv:
	@echo "Run: source venv/bin/activate"

cli:
	python -m pryces.presentation.console.cli

monitor:
	python -m pryces.presentation.scripts.monitor_stocks $(CONFIG)

test:
	pytest

format:
	black src/ tests/ --line-length 100
