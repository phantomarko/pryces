# Pryces

A Python CLI tool for retrieving stock price information, built with clean architecture principles.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Environment Configuration](#environment-configuration)
- [Usage](#usage)
  - [Interactive Menu](#interactive-menu)
  - [Monitor Stocks](#monitor-stocks)
  - [Get Stock Price](#get-stock-price)
  - [Get Multiple Stock Prices](#get-multiple-stock-prices)
  - [Test Notifications](#test-notifications)
- [Development](#development)
  - [Running Tests](#running-tests)
  - [Code Formatting with Black](#code-formatting-with-black)
  - [Working with Virtual Environment](#working-with-virtual-environment)
- [Project Principles](#project-principles)

## Overview

Pryces is a stock price information system that provides real-time and historical data for stocks through an interactive command-line interface. The project demonstrates clean architecture principles with clear separation of concerns and minimal dependencies.

## Architecture

This project follows clean architecture with clear separation of concerns:

- **Domain**: Core business logic and entities (framework-independent)
- **Application**: Use cases and application services
- **Infrastructure**: External dependencies (databases, APIs, file systems)
- **Presentation**: User interfaces (CLI, web, API endpoints)

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

The application loads these variables automatically from `.env` on startup via `python-dotenv`.

## Usage

### Interactive Menu

Launch the interactive menu system:

```bash
python -m pryces.presentation.console.cli
```

With verbose logging:
```bash
python -m pryces.presentation.console.cli --verbose
```

The interactive menu displays available commands and prompts for input:

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

  4. Test Notifications
     Send a test notification message

  0. Exit

Enter your selection:
```

### Monitor Stocks

When you select option 1, you'll be prompted to enter comma-separated stock symbols, an interval between checks (in seconds), and the number of repetitions:

```
--- Monitor Stocks ---

Enter stock symbols separated by commas (e.g., AAPL,GOOGL,MSFT): AAPL,GOOGL
Enter interval between checks in seconds (e.g., 90): 90
Enter number of repetitions (e.g., 525): 525
Executing...
```

Example output (with notifications):
```
Monitoring complete. 2 stocks checked, 1 notifications sent over 525 repetitions.
```

Example output (no notifications):
```
Monitoring complete. 2 stocks checked, 0 notifications sent over 525 repetitions.
```

**Notes:**
- This command monitors stocks and sends relevant notifications via Telegram
- The command repeats the check at the specified interval, useful for covering market hours (e.g., every 90 seconds from 09:00 to 22:00 = interval 90, repetitions 525)
- Duplicate notifications are automatically prevented
- Use `--verbose` to see each notification as it is sent in real time
- Make sure your `.env` file is configured with valid `TELEGRAM_BOT_TOKEN` and `TELEGRAM_GROUP_ID` values (see [Environment Configuration](#environment-configuration))

### Get Stock Price

When you select option 2, you'll be prompted to enter a stock symbol:

```
--- Get Stock Price ---

Enter stock symbol (e.g., AAPL, GOOGL): AAPL
Executing...
```

Example output (success):
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

**Note:** Only `symbol` and `currentPrice` are required fields. All other fields are optional and will be omitted if data is unavailable.

Example output (error):
```
Error: Stock not found: INVALID
```

After each command execution, the menu returns to the main selection screen. Select `0` to exit the program.

### Get Multiple Stock Prices

When you select option 3, you'll be prompted to enter comma-separated stock symbols:

```
--- Get Multiple Stock Prices ---

Enter stock symbols separated by commas (e.g., AAPL,GOOGL,MSFT): AAPL,GOOGL,MSFT
Executing...
```

Example output (success with all symbols found):
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

Example output (partial success with some invalid symbols):
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

============================================================
Summary: 3 requested, 1 successful, 2 failed
```

**Notes:**
- Only `symbol` and `currentPrice` are required fields. All other fields are optional and will be omitted if data is unavailable.
- Invalid symbols are silently skipped and do not cause errors. Check the summary line to see how many symbols succeeded vs. failed.

### Test Notifications

When you select option 4, a test notification message is sent automatically (no input required):

```
--- Test Notifications ---

Executing...
```

Example output (success):
```
Test notification sent successfully.
```

Example output (failure):
```
Test notification failed.
```

**Note:** This command sends a test message via the Telegram Bot API. Make sure your `.env` file is configured with valid `TELEGRAM_BOT_TOKEN` and `TELEGRAM_GROUP_ID` values (see [Environment Configuration](#environment-configuration)).

## Development

### Running Tests

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/application/use_cases/get_stock_price/test_get_stock_price.py -v
```

Run tests with coverage:
```bash
pytest --cov=pryces --cov-report=html
```

### Code Formatting with Black

This project uses [Black](https://black.readthedocs.io/) for consistent code formatting.

**Automatic Formatting (Recommended):**

Install the pre-commit hook to automatically format code on every commit:
```bash
cp scripts/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Once installed, Black will automatically format your staged Python files and include them in your commit.

**Manual Formatting:**

Format all source and test files:
```bash
black src/ tests/
```

Check formatting without making changes:
```bash
black --check src/ tests/
```

Preview formatting changes:
```bash
black --diff src/ tests/
```

Format a specific file:
```bash
black src/pryces/domain/entities.py
```

**Configuration:**

Black is configured in `pyproject.toml` with:
- Line length: 100 characters
- Target Python versions: 3.11, 3.12

### Working with Virtual Environment

Activate the virtual environment before running tests or installing dependencies:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Deactivate when done:
```bash
deactivate
```

## Project Principles

See [CLAUDE.md](CLAUDE.md) for detailed conventions and architectural guidelines.
