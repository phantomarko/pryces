# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository (Pryces) is currently empty and awaiting initialization.

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

## Next Steps

Once the project is initialized, update this file with:
- Build and test commands
- Project architecture and structure
- Development workflow
