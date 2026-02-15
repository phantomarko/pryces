# Pryces

Retrieves real-time stock data from Yahoo Finance, tracks moving average crossovers and significant price movements, and delivers Telegram notifications when relevant market events occur.

## Table of Contents

- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
- [Usage](#usage)
  - [Scripts](#scripts)
    - [Monitor Stocks Script](#monitor-stocks-script)
  - [Interactive CLI](#interactive-cli)
    - [Monitor Stocks](#monitor-stocks)
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
| `LOGS_DIRECTORY` | Directory path for log file output (optional — if not set, file logging is disabled) |

The application loads these variables automatically from `.env` on startup via `python-dotenv`.

## Usage

Pryces provides two ways to interact with stock data: **standalone scripts** for automated or scheduled tasks, and an **interactive CLI** with a menu-driven interface.

### Scripts

Standalone scripts for automated or scheduled execution. Unlike the interactive CLI, scripts are configured via files and designed to run unattended (e.g., via cron).

#### Monitor Stocks Script

Monitors stocks and sends Telegram notifications, driven by a JSON configuration file.

```bash
python -m pryces.presentation.scripts.monitor_stocks monitor.json.example
make monitor  # alternative using Makefile (defaults to monitor.json.example)
make monitor CONFIG=monitor_alternative.json  # alternative with custom config
```

Run in the background (detached from the terminal):
```bash
nohup python -m pryces.presentation.scripts.monitor_stocks monitor.json &
```

Set `LOGS_DIRECTORY` in your `.env` file before launching it so you can follow the process after closing the terminal. Log files are created with a timestamp. To check the log:
```bash
tail -f /tmp/pryces_20260212_143025.log
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

**Notes:**
- Duplicate notifications are automatically prevented within the same run
- Make sure your `.env` file is configured with valid `TELEGRAM_BOT_TOKEN` and `TELEGRAM_GROUP_ID` values (see [Environment Configuration](#environment-configuration))

### Interactive CLI

Launch the interactive menu:

```bash
python -m pryces.presentation.console.cli
make cli  # alternative using Makefile
```

The menu displays available commands and prompts for input:

```
============================================================
PRYCES - Stock Price Information System
============================================================

Available Commands:

  1. Monitor Stocks
     Monitor stocks for relevant price notifications

  2. Get Stock Price
     Retrieve current price and details for a single stock symbol

  3. Get Multiple Stock Prices
     Retrieve current prices for multiple stock symbols

  4. Check Readiness
     Check if all components and configs are ready for monitoring

  0. Exit

Enter your selection:
```

### Monitor Stocks

Launches the [Monitor Stocks Script](#monitor-stocks-script) as a detached background process. The CLI remains responsive after launching.

When you select option 1, you'll be prompted to enter the path to a JSON config file (see [Monitor Stocks Script](#monitor-stocks-script) for the config format):

```
--- Monitor Stocks ---

Enter the path to the JSON config file (e.g., monitor.json): monitor.json.example
Executing...
```

Example output:
```
Monitor started in background (PID: 12345)
```

The returned PID can be used to check or stop the process (e.g., `kill 12345`).

### Get Stock Price

Retrieves current price and market details for a single stock symbol.

When you select option 2, you'll be prompted to enter a stock symbol:

```
--- Get Stock Price ---

Enter stock symbol (e.g., AAPL, GOOGL): AAPL
Executing...
```

Example output:
```
AAPL - Apple Inc. (USD)

  Market State:        OPEN
  Current Price:       269.48
  Previous Close:      269.955
  Open:                269.13
  Day High:            271.875
  Day Low:             267.61
  50-Day Average:      268.3466
  200-Day Average:     236.9913
  52-Week High:        288.62
  52-Week Low:         169.21
```

After each command execution, the menu returns to the main selection screen. Select `0` to exit the program.

### Get Multiple Stock Prices

Retrieves current prices for multiple stock symbols at once, with a summary of successful and failed lookups.

When you select option 3, you'll be prompted to enter comma-separated stock symbols:

```
--- Get Multiple Stock Prices ---

Enter stock symbols separated by commas (e.g., AAPL,GOOGL,MSFT): AAPL,GOOGL,MSFT
Executing...
```

Example output:
```
AAPL - Apple Inc. (USD)

  Market State:        OPEN
  Current Price:       269.48
  Previous Close:      269.955
  Open:                269.13
  Day High:            271.875
  Day Low:             267.61
  50-Day Average:      268.3466
  200-Day Average:     236.9913
  52-Week High:        288.62
  52-Week Low:         169.21

------------------------------------------------------------

GOOGL - Alphabet Inc. (USD)

  Market State:        OPEN
  Current Price:       202.63
  Previous Close:      202.75
  Open:                202.13
  Day High:            204.06
  Day Low:             201.32
  50-Day Average:      194.5574
  200-Day Average:     178.4237
  52-Week High:        207.18
  52-Week Low:         137.82

------------------------------------------------------------

MSFT - Microsoft Corporation (USD)

  Market State:        OPEN
  Current Price:       434.28
  Previous Close:      435.47
  Open:                432.40
  Day High:            435.95
  Day Low:             429.90
  50-Day Average:      436.8654
  200-Day Average:     433.2095
  52-Week High:        468.35
  52-Week Low:         385.58

============================================================
Summary: 3 requested, 3 successful, 0 failed
```

### Check Readiness

Verifies that all components and configurations are ready for a successful monitoring session. Checks environment variables and Telegram connectivity.

When you select option 4, all checks run automatically (no input required):

```
--- Check Readiness ---

Executing...
```

Example output when everything is configured correctly:
```
[READY] Environment variables
[READY] Telegram notifications
```

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
