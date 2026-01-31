# Pryces

A Python project built with clean architecture principles.

## Architecture

This project follows clean architecture with clear separation of concerns:

- **Domain**: Core business logic and entities (framework-independent)
- **Application**: Use cases and application services
- **Infrastructure**: External dependencies (databases, APIs, file systems)
- **Presentation**: User interfaces (CLI, web, API endpoints)

## Setup

### Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install development dependencies
```bash
pip install -e ".[dev]"
```

## Development

### Run tests
```bash
pytest
```

### Run tests with coverage
```bash
pytest --cov=pryces --cov-report=html
```

## Project Principles

See [CLAUDE.md](CLAUDE.md) for detailed conventions and architectural guidelines.
