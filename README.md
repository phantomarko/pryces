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

### Get Stock Price

Retrieve stock price information via command line:

```bash
python -m pryces.presentation.console.cli AAPL
```

With verbose logging (logs go to stderr, JSON to stdout):
```bash
python -m pryces.presentation.console.cli AAPL --verbose
```

Example output (success):
```json
{
  "success": true,
  "data": {
    "ticker": "AAPL",
    "price": "150.25",
    "currency": "USD"
  }
}
```

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

## Project Principles

See [CLAUDE.md](CLAUDE.md) for detailed conventions and architectural guidelines.
