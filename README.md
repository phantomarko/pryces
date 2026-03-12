# Pryces

Retrieves real-time stock data from Yahoo Finance and delivers Telegram notifications when relevant market events occur.

## Table of Contents

- [Overview](#overview)
- [Tracked Notifications](#tracked-notifications)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
- [Usage](#usage)
  - [Scripts](#scripts)
    - [Monitor Stocks](#monitor-stocks)
    - [Telegram Bot](#telegram-bot)
  - [Interactive CLI](#interactive-cli)
    - [List Configs](#list-configs)
    - [Create Config](#create-config)
    - [Edit Config](#edit-config)
    - [Delete Config](#delete-config)
    - [Execute Monitor Process](#execute-monitor-process)
    - [List Monitor Processes](#list-monitor-processes)
    - [Stop Monitor Process](#stop-monitor-process)
    - [Get Stock Prices](#get-stock-prices)
    - [Check Readiness](#check-readiness)
- [Contributing](#contributing)
- [License](#license)

## Overview

Pryces uses **Yahoo Finance** as its data source, which means you can monitor virtually any asset class available on the Yahoo Finance website — stocks, ETFs, indexes, mutual funds, cryptocurrencies, currencies, futures, commodities, and more — simply by using the same symbol as shown there (e.g. `AAPL`, `BTC-USD`, `^GSPC`, `GC=F`, `EURUSD=X`).

The monitoring tool is designed around the concept of a **daily market session**. Each monitor process tracks one session: it detects market opens, closes, and price milestones throughout that session. When the session ends the process exits, resetting all deduplication state and transition tracking so the next run starts clean for the following session. Despite this session-scoped design, a **single monitor process can track assets from all world markets simultaneously**, since each symbol is queried independently.

> **Linux only**: Pryces has been developed and tested on Linux. All commands and setup steps in this document target Linux systems. Users on other operating systems may need to adapt them accordingly.

## Tracked Notifications

The following events are detected and sent as Telegram messages during a monitoring run:

- Market open / market closed
- Price is close to crossing the 50-day or 200-day moving average (within 2.5%)
- Price crossed the 50-day or 200-day moving average
- Price moved more than 5%, 10%, 15%, or 20% from the previous close (up or down)
- Session gains erased (price crossed back below 0% after a positive percentage threshold)
- Session losses erased (price crossed back above 0% after a negative percentage threshold)
- Price set a new 52-week high or low (compared to the previous monitoring run)
- Price reached a configured target level

## Getting Started

### Requirements

- Python 3.11 or higher

### Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the project in development mode:
```bash
pip install -e ".[dev]"
```

This will install:
- The `pryces` package in editable mode
- Development dependencies (pytest, etc.)

### Environment Configuration

Pryces uses environment variables for external service configuration. Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

| Variable | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your Telegram Bot API token (from [@BotFather](https://t.me/BotFather)) |
| `TELEGRAM_GROUP_ID` | The Telegram group/chat ID where notifications are sent |
| `MAX_FETCH_WORKERS` | Maximum number of concurrent workers for fetching stock data (values above 6 are not recommended on low-resource systems) |
| `LOGS_DIRECTORY` | Directory path for log file output (use `/tmp` if you don't need persistent logs) |

The application loads these variables automatically from `.env` on startup via `python-dotenv`.

## Usage

Pryces provides two ways to interact with stock data: **standalone scripts** for automated or scheduled tasks, and an **interactive CLI** with a menu-driven interface.

### Scripts

Standalone scripts for automated or scheduled execution. Unlike the interactive CLI, scripts are configured via files and designed to run unattended (e.g., via cron).

#### Monitor Stocks

Monitors stocks and sends Telegram notifications, driven by a JSON configuration file.

```bash
# using Makefile
make monitor                                      # defaults to configs/example.json, 1 minute
make monitor DURATION=30                          # monitor for 30 minutes
make monitor CONFIG=monitor_alternative.json DURATION=60
make monitor DURATION=30 EXTRA_DELAY=5            # add 5 minutes to the price delay

# or using Python
source venv/bin/activate
python -m pryces.presentation.scripts.monitor_stocks configs/example.json --duration 30
python -m pryces.presentation.scripts.monitor_stocks configs/example.json --duration 60 --extra-delay 5
```

Run in the background (detached from the terminal):
```bash
# using Makefile
nohup make monitor CONFIG=monitor_alternative.json DURATION=60 &

# or using Python
source venv/bin/activate
nohup python -m pryces.presentation.scripts.monitor_stocks configs/example.json --duration 60 &
```

**Arguments:**

| Python argument | Makefile variable | Description |
|---|---|---|
| `config` | `CONFIG` | Path to the JSON configuration file (required, defaults to `configs/example.json` in Makefile) |
| `--duration N` | `DURATION=N` | Monitoring duration in minutes (required, defaults to `1` in Makefile) |
| `--extra-delay N` | `EXTRA_DELAY=N` | Extra minutes added to the exchange-reported price delay. Only applied when the exchange already reports a non-zero delay. Defaults to `0`. |

Log files are created with a timestamp. To check the log:
```bash
tail -f /tmp/pryces_monitor_20260212_143025.log
```

**Configuration file format** (see `configs/example.json`):

```json
{
    "interval": 5,
    "symbols": [
        {"symbol": "AAPL", "prices": [150.0, 200.0]},
        {"symbol": "GOOGL", "prices": [100.0]}
    ]
}
```

| Field | Type | Description |
|---|---|---|
| `interval` | int | Seconds to wait between cycles |
| `symbols` | list[object] | Symbols to monitor, each with a `symbol` string and a `prices` list of target price levels |

The `prices` list under each symbol defines **target price levels**. When a target is reached, it is automatically removed from the config file — the symbol itself is kept even if all its prices are fulfilled, so it continues to be monitored for all other notification types.

The **configuration file is re-read on every monitoring cycle**, so you can edit `interval` or `symbols` while the script is running and the changes will take effect on the next iteration — no restart required.

See [Tracked Notifications](#tracked-notifications) for the full list of events detected and sent during a run.

#### Telegram Bot

Listens for commands in the configured Telegram group and manages target prices in config files — listing, adding, and removing targets without leaving Telegram. The bot locates the config containing the given symbol automatically (first alphabetical match wins).

```bash
# using Makefile
make bot
make bot VERBOSE=1

# or using Python
source venv/bin/activate
python -m pryces.presentation.scripts.telegram_bot
python -m pryces.presentation.scripts.telegram_bot --verbose
```

**Available commands** (sent as messages in the Telegram group):

| Command | Description |
|---|---|
| `/symbols` | List all tracked symbols across configs |
| `/targets <symbol>` | List all target prices for a symbol |
| `/target_add <symbol> <price>` | Add a target price to a symbol |
| `/target_remove <symbol> <price>` | Remove a specific target price from a symbol |
| `/help` | Show all commands with usage |

Messages from chats other than `TELEGRAM_GROUP_ID` are silently ignored. The bot uses long-polling (`getUpdates`) — no webhook or public URL is required.

### Interactive CLI

Launch the interactive menu:

```bash
# using Makefile
make cli

# or using Python
source venv/bin/activate
python -m pryces.presentation.console.cli
```

Available commands:

| # | Command | Description |
|---|---------|-------------|
| 1 | List Configs | List all configs in the `configs/` directory |
| 2 | Create Config | Create a new monitoring config |
| 3 | Edit Config | Edit interval or symbols of an existing config |
| 4 | Delete Config | Delete an existing config |
| 5 | Execute Monitor Process | Launch stock monitor as background process |
| 6 | List Monitor Processes | List running monitor processes |
| 7 | Stop Monitor Process | Stop a running monitor process |
| 8 | Get Stock Prices | Current price and details for one or multiple symbols |
| 9 | Check Readiness | Verify env vars and Telegram connectivity |
| 0 | Exit | Exit the program |

Configs are stored in the `configs/` directory at the project root. Use the CLI to create and manage them — there is no need to edit JSON files manually.

#### List Configs

Lists all configs in `configs/`, showing interval and symbols with target prices for each.

```
1. Config: portfolio.json
  Interval: 60s
  Symbols:
    AAPL: 150, 160
    MSFT
```

#### Create Config

Prompts for a name (without `.json`), interval in seconds, and symbols with optional target prices.

```
Config name (without .json): portfolio
Interval in seconds: 60
Symbols (e.g. AAPL MSFT:150,155 GOOG): AAPL MSFT:150,155.50 GOOG
```

```
Config created: /path/to/configs/portfolio.json
```

Symbols format: space-separated tokens where each token is either `SYMBOL` or `SYMBOL:P1,P2,...`.

#### Edit Config

Picks from existing configs, then lets you change either the interval or the symbols/targets.

```
Found 2 config(s):

1. Config: portfolio.json
  Interval: 60s
  Symbols:
    AAPL: 150, 160
    MSFT

2. Config: watchlist.json
  Interval: 30s
  Symbols:
    GOOGL

Select config (1-2): 1
What to edit: 1=interval  2=symbols and targets
What to edit (1 or 2): 2
Symbols: AAPL:200 MSFT GOOG:150,160
```

```
Config updated: portfolio.json
```

#### Delete Config

Picks from existing configs and prompts for confirmation before deleting.

```
Found 1 config(s):
  1. portfolio.json

Select config to delete (1-1): 1
Type 'yes' to confirm deletion: yes
```

```
Config deleted: portfolio.json
```

#### Execute Monitor Process

Picks from configs in `configs/`, then prompts for duration and optional extra delay. Launches the [Monitor Stocks](#monitor-stocks) as a detached background process.

```
Found 1 config(s):
  1. portfolio.json

Select config (1-1): 1
Monitoring duration in minutes: 60
Extra price delay in minutes [0]: 5
```

```
Monitor started in background (PID: 12345)
```

The returned PID can be used to check or stop the process (e.g., `kill 12345`). Leave the delay field empty to use the default of `0`.

#### List Monitor Processes

Lists all running monitor processes on the machine. No input required.

Example output:
```
Found 2 monitor process(es):
  1. PID 12345 — config: /path/to/config.json
  2. PID 67890 — config: /path/to/other.json
```

If no monitors are running:
```
No monitor processes found.
```

#### Stop Monitor Process

Lists running monitor processes with numbers and prompts to pick one to stop. No pre-collected input required.

Example interaction:
```
Found 2 monitor process(es):
  1. PID 12345 — config: /path/to/config.json
  2. PID 67890 — config: /path/to/other.json

Enter number to stop (1-2, 0 to cancel): 1
```

Example output:
```
Stopped monitor process PID 12345 (config: /path/to/config.json).
```

Enter `0` to cancel without stopping anything.

#### Get Stock Prices

Retrieves current price and market details for one or multiple stock symbols. Enter a single symbol or a space-separated list.

```
Enter stock symbols separated by spaces (e.g., AAPL GOOGL MSFT): AAPL
```

Example output for a single symbol:
```
AAPL - Apple Inc. (USD)

  Market State:       OPEN
  Current Price:      269.48
  Previous Close:     269.955
  Open:               269.13
  Day High:           271.875
  Day Low:            267.61
  50-Day Average:     268.3466
  200-Day Average:    236.9913
  52-Week High:       288.62
  52-Week Low:        169.21
  Price delay (min):  0
```

When fetching multiple symbols, each result is separated by a divider line, followed by a summary:

```
Enter stock symbols separated by spaces (e.g., AAPL GOOGL MSFT): AAPL GOOGL MSFT
```

```
Summary: 3 requested, 3 successful, 0 failed
```

#### Check Readiness

Verifies that all components and configurations are ready for monitoring. Runs automatically with no input required.

Example output when issues are detected:
```
[NOT READY] Environment variables
  - TELEGRAM_BOT_TOKEN is missing or empty
  - MAX_FETCH_WORKERS is missing or not a valid integer
[NOT READY] Telegram notifications

Fix the errors above and restart the app for changes to take effect.
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for architecture details, development workflow, and project conventions.

## License

This project is licensed under the [MIT License](LICENSE).
