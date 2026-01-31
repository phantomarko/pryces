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

## Project Principles

See [CLAUDE.md](CLAUDE.md) for detailed conventions and architectural guidelines.
