# Contributing to Pryces

Guidelines for developing, testing, and contributing to the project.

## Table of Contents

- [Architecture](#architecture)
- [Development Workflow](#development-workflow)
  - [Virtual Environment](#virtual-environment)
  - [Running Tests](#running-tests)
  - [Code Formatting](#code-formatting)
- [Project Conventions](#project-conventions)

## Architecture

Pryces follows a **Ports & Adapters** (hexagonal) architecture with four layers:

```
Presentation → Application → Domain
                   ↑
            Infrastructure (implements application ports)
```

- **Domain**: Core business logic and entities (framework-independent)
- **Application**: Use cases, services, and port interfaces (ABCs)
- **Infrastructure**: Adapter implementations for external dependencies (APIs, databases)
- **Presentation**: User interfaces (CLI)

See [CLAUDE.md](CLAUDE.md) for detailed architectural mapping, key patterns, and file-level breakdown.

## Development Workflow

### Virtual Environment

Activate before running tests or installing dependencies:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Deactivate when done:

```bash
deactivate
```

### Running Tests

```bash
# Run all tests
pytest
make test  # alternative using Makefile

# Verbose output
pytest -v

# Specific test file
pytest tests/application/use_cases/get_stock_price/test_get_stock_price.py -v

# With coverage report
pytest --cov=pryces --cov-report=html
```

### Code Formatting

This project uses [Black](https://black.readthedocs.io/) for consistent code formatting, configured in `pyproject.toml` with line length 100 and target Python 3.11/3.12.

**Automatic formatting (recommended)** — install the pre-commit hook:

```bash
cp scripts/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Manual formatting:**

```bash
# Format all files
black src/ tests/
make format  # alternative using Makefile

# Check without changes
black --check src/ tests/

# Preview changes
black --diff src/ tests/
```

## Project Conventions

- **Minimal dependencies**: Prefer built-in features over external libraries. Only add a dependency when there's no reasonable alternative.
- **Self-documenting code**: Use clear names, structure, and type hints. Comments explain *why*, not *what*.
- **Conventional Commits**: Use `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:` prefixes.

See [CLAUDE.md](CLAUDE.md) for the complete set of conventions and guidelines.
