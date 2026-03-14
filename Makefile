DURATION ?= 1
DEBUG_FLAG := $(if $(DEBUG),--debug,)
VERBOSE_FLAG := $(if $(VERBOSE),--verbose,)
EXTRA_DELAY_FLAG := $(if $(EXTRA_DELAY),--extra-delay $(EXTRA_DELAY),)
VENV := venv/bin

.PHONY: cli monitor bot test format

cli:
	$(VENV)/python -m pryces.presentation.console.cli $(DEBUG_FLAG)

monitor:
ifndef CONFIG
	$(error CONFIG is required. Usage: make monitor CONFIG=configs/myconfig.json)
endif
	$(VENV)/python -m pryces.presentation.scripts.monitor_stocks $(CONFIG) --duration $(DURATION) $(DEBUG_FLAG) $(VERBOSE_FLAG) $(EXTRA_DELAY_FLAG)

bot:
	$(VENV)/python -m pryces.presentation.scripts.telegram_bot $(DEBUG_FLAG) $(VERBOSE_FLAG)

test:
	$(VENV)/pytest

format:
	$(VENV)/black src/ tests/ --line-length 100
