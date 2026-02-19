# Pryces

Retrieves real-time stock data from Yahoo Finance, tracks moving average crossovers and significant price movements, and delivers Telegram notifications when relevant market events occur.

## Table of Contents

- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
- [Usage](#usage)
  - [Scripts](#scripts)
    - [Monitor Stocks](#monitor-stocks)
  - [Interactive CLI](#interactive-cli)
    - [Monitor Stocks (CLI)](#monitor-stocks-cli)
    - [List Monitor Processes](#list-monitor-processes)
    - [Get Stock Price](#get-stock-price)
    - [Get Multiple Stock Prices](#get-multiple-stock-prices)
    - [Check Readiness](#check-readiness)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Requirements

- Python 3.11 or higher

### Installation

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
make monitor  # defaults to monitor.json.example
make monitor CONFIG=monitor_alternative.json  # alternative with custom config

# or using Python
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m pryces.presentation.scripts.monitor_stocks monitor.json.example
```

Run in the background (detached from the terminal):
```bash
# using Makefile
nohup make monitor CONFIG=monitor_alternative.json &

# or using Python
source venv/bin/activate  # On Windows: venv\Scripts\activate
nohup python -m pryces.presentation.scripts.monitor_stocks monitor.json.example &
```

Log files are created with a timestamp. To check the log:
```bash
tail -f /tmp/pryces_monitor_20260212_143025.log
```

**Configuration file format** (see `monitor.json.example`):

```json
{
    "duration": 2,
    "interval": 5,
    "symbols": ["AAPL", "GOOGL"]
}
```

| Field | Type | Description |
|---|---|---|
| `duration` | int | Monitoring duration in minutes |
| `interval` | int | Seconds to wait between cycles |
| `symbols` | list[str] | Stock symbols to monitor |

**Tracked notifications:**
- Market open / market closed
- Price is close to crossing the 50-day or 200-day moving average (within 5%)
- Price crossed the 50-day or 200-day moving average
- Price moved more than 5%, 10%, 15%, or 20% from the previous close (up or down)
- Price set a new 52-week high or low (compared to the previous monitoring run)

**Notes:**
- Duplicate notifications are automatically prevented within the same run
- When a stock reports a non-zero `priceDelayInMinutes` (e.g. 15 for delayed exchanges), notifications are suppressed for that many minutes after a market state transition to OPEN or POST. This prevents sending stale prices at the exact moment the market opens or closes — once the delay has elapsed, notifications fire normally with fresh data.
- Make sure your `.env` file is configured with valid `TELEGRAM_BOT_TOKEN` and `TELEGRAM_GROUP_ID` values (see [Environment Configuration](#environment-configuration))

### Interactive CLI

Launch the interactive menu:

```bash
# using Makefile
make cli

# or using Python
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m pryces.presentation.console.cli
```

Available commands:

| # | Command | Description |
|---|---------|-------------|
| 1 | Monitor Stocks | Launch stock monitor as background process |
| 2 | List Monitor Processes | List running monitor processes |
| 3 | Stop Monitor Process | Stop a running monitor process |
| 4 | Get Stock Price | Current price and details for one symbol |
| 5 | Get Multiple Stock Prices | Current prices for multiple symbols |
| 6 | Check Readiness | Verify env vars and Telegram connectivity |
| 0 | Exit | Exit the program |

#### Monitor Stocks (CLI)

Launches the [Monitor Stocks](#monitor-stocks) as a detached background process. See that section for config format and notification details.

```
Enter the path to the JSON config file (e.g., monitor.json): monitor.json.example
```

```
Monitor started in background (PID: 12345)
```

The returned PID can be used to check or stop the process (e.g., `kill 12345`).

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

#### Get Stock Price

Retrieves current price and market details for a single stock symbol.

```
Enter stock symbol (e.g., AAPL, GOOGL): AAPL
```

Example output:
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

#### Get Multiple Stock Prices

Retrieves current prices for multiple stock symbols at once. Outputs each stock in the same format as [Get Stock Price](#get-stock-price), separated by a divider line, followed by a summary:

```
Enter stock symbols separated by commas (e.g., AAPL,GOOGL,MSFT): AAPL,GOOGL,MSFT
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
