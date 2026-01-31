# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pryces is a Python project built with clean architecture principles, emphasizing SOLID design, minimal dependencies, and clear separation of concerns.

## Patterns and Conventions

### SOLID Principles
This project adheres to SOLID principles:
- **S**ingle Responsibility Principle
- **O**pen/Closed Principle
- **L**iskov Substitution Principle
- **I**nterface Segregation Principle
- **D**ependency Inversion Principle

### Dependency Management
- Minimize use of third-party packages
- Only add external dependencies when:
  - There is no reasonable alternative to implement the functionality
  - The package is secure, well-maintained, and clearly the best option for the use case
- Prefer built-in language/platform features over external libraries

### Clean Architecture
Follow clean architecture principles to create a resilient, scalable, and maintainable codebase:
- Separate concerns into distinct layers (domain, application, infrastructure, presentation)
- Keep business logic independent of frameworks, databases, and external agencies
- Use dependency inversion to point dependencies inward toward the domain
- Write testable code with clear boundaries between layers
- Design for change and evolution
- Create a codebase that any skilled developer would appreciate working with

## Architecture

The project follows a layered clean architecture approach:

### Layer Structure
```
src/pryces/
├── domain/          # Core business logic (no external dependencies)
├── application/     # Use cases and application services
├── infrastructure/  # External dependencies (DB, APIs, file systems)
└── presentation/    # User interfaces (CLI, web, API)
```

### Dependency Rules
- **Domain**: No dependencies on other layers (pure business logic)
- **Application**: Depends only on Domain
- **Infrastructure**: Implements interfaces defined in Domain/Application
- **Presentation**: Depends on Application (calls use cases)

Dependencies always point inward (Presentation → Application → Domain).

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=pryces --cov-report=html

# Run specific test file
pytest tests/domain/test_example.py

# Run specific test function
pytest tests/domain/test_example.py::test_function_name
```

### Code Quality
```bash
# Type checking (if mypy is added)
mypy src/pryces

# Run tests in watch mode (if pytest-watch is added)
ptw
```

## Development Workflow

1. Write tests first (TDD approach recommended)
2. Implement features starting from the domain layer outward
3. Use dependency injection for infrastructure dependencies
4. Keep the domain layer pure and testable
5. Follow conventional commits for all commit messages
