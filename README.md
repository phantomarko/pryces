# Pryces

A Python project built with clean architecture principles.

## Architecture

This project follows clean architecture with clear separation of concerns:

- **Domain**: Core business logic and entities (framework-independent)
- **Application**: Use cases and application services
- **Infrastructure**: External dependencies (databases, APIs, file systems)
- **Presentation**: User interfaces (CLI, web, API endpoints)

## Setup

### Quick Start

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

### Working with Virtual Environment

Activate the virtual environment before running tests or installing dependencies:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Deactivate when done:
```bash
deactivate
```

## Console Commands

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

  1. Get Stock Price
     Retrieve current price and details for a single stock symbol

  2. Get Multiple Stock Prices
     Retrieve current prices for multiple stock symbols

  0. Exit

Enter your selection:
```

### Get Stock Price

When you select option 1, you'll be prompted to enter a stock symbol:

```
--- Get Stock Price ---

Enter stock symbol (e.g., AAPL, GOOGL): AAPL
Executing...
```

Example output (success):
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "currentPrice": "269.48",
    "name": "Apple Inc.",
    "currency": "USD",
    "previousClosePrice": "269.955",
    "openPrice": "269.13",
    "dayHigh": "271.875",
    "dayLow": "267.61",
    "fiftyDayAverage": "268.3466",
    "twoHundredDayAverage": "236.9913",
    "fiftyTwoWeekHigh": "288.62",
    "fiftyTwoWeekLow": "169.21"
  }
}
```

**Note:** Only `symbol` and `currentPrice` are required fields. All other fields are optional and may be `null` if data is unavailable.

Example output (error):
```json
{
  "success": false,
  "error": {
    "code": "STOCK_NOT_FOUND",
    "message": "Stock not found: INVALID"
  }
}
```

After each command execution, the menu returns to the main selection screen. Select `0` to exit the program.

### Get Multiple Stock Prices

When you select option 2, you'll be prompted to enter comma-separated stock symbols:

```
--- Get Multiple Stock Prices ---

Enter stock symbols separated by commas (e.g., AAPL,GOOGL,MSFT): AAPL,GOOGL,MSFT
Executing...
```

Example output (success with all symbols found):
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "currentPrice": "269.48",
      "name": "Apple Inc.",
      "currency": "USD",
      "previousClosePrice": "269.955",
      "openPrice": "269.13",
      "dayHigh": "271.875",
      "dayLow": "267.61",
      "fiftyDayAverage": "268.3466",
      "twoHundredDayAverage": "236.9913",
      "fiftyTwoWeekHigh": "288.62",
      "fiftyTwoWeekLow": "169.21"
    },
    {
      "symbol": "GOOGL",
      "currentPrice": "202.63",
      "name": "Alphabet Inc.",
      "currency": "USD",
      "previousClosePrice": "202.75",
      "openPrice": "202.13",
      "dayHigh": "204.06",
      "dayLow": "201.32",
      "fiftyDayAverage": "194.5574",
      "twoHundredDayAverage": "178.4237",
      "fiftyTwoWeekHigh": "207.18",
      "fiftyTwoWeekLow": "137.82"
    },
    {
      "symbol": "MSFT",
      "currentPrice": "434.28",
      "name": "Microsoft Corporation",
      "currency": "USD",
      "previousClosePrice": "435.47",
      "openPrice": "432.40",
      "dayHigh": "435.95",
      "dayLow": "429.90",
      "fiftyDayAverage": "436.8654",
      "twoHundredDayAverage": "433.2095",
      "fiftyTwoWeekHigh": "468.35",
      "fiftyTwoWeekLow": "385.58"
    }
  ],
  "summary": {
    "requested": 3,
    "successful": 3,
    "failed": 0
  }
}
```

Example output (partial success with some invalid symbols):
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "currentPrice": "269.48",
      "name": "Apple Inc.",
      "currency": "USD",
      "previousClosePrice": "269.955",
      "openPrice": "269.13",
      "dayHigh": "271.875",
      "dayLow": "267.61",
      "fiftyDayAverage": "268.3466",
      "twoHundredDayAverage": "236.9913",
      "fiftyTwoWeekHigh": "288.62",
      "fiftyTwoWeekLow": "169.21"
    }
  ],
  "summary": {
    "requested": 3,
    "successful": 1,
    "failed": 2
  }
}
```

**Notes:**
- Only `symbol` and `currentPrice` are required fields. All other fields are optional and may be `null` if data is unavailable.
- Invalid symbols are silently skipped and do not cause errors. Check the `summary` section to see how many symbols succeeded vs. failed.
- The `summary` includes:
  - `requested`: Total number of symbols requested
  - `successful`: Number of symbols successfully fetched
  - `failed`: Number of symbols that failed (invalid or data unavailable)

## Project Principles

See [CLAUDE.md](CLAUDE.md) for detailed conventions and architectural guidelines.
