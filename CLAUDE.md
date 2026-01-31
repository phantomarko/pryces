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

### Dependency Rules
- **Domain**: No dependencies on other layers (pure business logic)
- **Application**: Depends only on Domain
- **Infrastructure**: Implements interfaces defined in Domain/Application
- **Presentation**: Depends on Application (calls use cases)

Dependencies always point inward (Presentation → Application → Domain).

**Note**: For setup and testing commands, see [README.md](README.md).

## Development Workflow

1. Write tests first (TDD approach recommended)
2. Implement features starting from the domain layer outward
3. Use dependency injection for infrastructure dependencies
4. Keep the domain layer pure and testable
5. Follow conventional commits for all commit messages

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>: <description>

[optional body]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring (no functional changes)
- `test`: Adding or updating tests
- `docs`: Documentation changes
- `chore`: Maintenance tasks (dependencies, config, etc.)
- `style`: Code style/formatting changes
- `perf`: Performance improvements

**Examples:**
```
feat: add GetStockPrice use case with provider interface
fix: handle null response from stock price provider
test: add unit tests for StockNotFound exception
chore: update README with testing instructions
refactor: extract mock provider to setup method
```
