# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pryces is a Python project built with clean architecture principles, emphasizing SOLID design, minimal dependencies, and clear separation of concerns.

## Critical Directives

### Update README.md After Changes
**IMPORTANT**: Whenever you make significant changes to the codebase (new features, API changes, new fields, renamed parameters, etc.), you MUST update the README.md to reflect these changes:
- Update example outputs to match current JSON structure
- Update command examples if CLI arguments change
- Add documentation for new features
- Ensure all examples are accurate and tested

The README is user-facing documentation and must stay synchronized with the actual code behavior.

### Prefer Using Subagents for Context Optimization
**IMPORTANT**: Always use specialized subagents (via the Task tool) whenever possible to optimize context usage, unless explicitly instructed not to use subagents.

Use subagents for:
- **Exploration tasks**: Understanding codebase structure, finding patterns, locating functionality
- **Search operations**: Multi-step searches across files, grep operations with follow-up analysis
- **Planning**: Complex implementation plans that require code exploration
- **Research**: Investigating how features work, tracing dependencies
- **Parallel work**: Independent tasks that can run simultaneously

Only work directly (without subagents) when:
- User explicitly requests direct execution
- Task is trivial (single file read/write)
- Already in a subagent context

This helps maintain clean context and allows better task delegation.

### Prefer Using Plan Mode for Non-Trivial Tasks
**IMPORTANT**: Always use plan mode (EnterPlanMode) for implementation tasks unless explicitly instructed not to or the task is trivial.

Use plan mode for:
- **New features**: Adding any new functionality beyond single-line changes
- **Code modifications**: Changes affecting multiple files or existing behavior
- **Refactoring**: Restructuring code or changing architecture
- **Multi-step implementations**: Tasks requiring more than 2-3 simple steps
- **Uncertain scope**: When you need to explore before understanding full requirements

Do NOT use plan mode for:
- User explicitly requests direct implementation
- Trivial tasks (typo fixes, single-line changes, obvious bugs)
- Pure research/exploration (use Task tool with Explore agent instead)
- Tasks with very specific, detailed instructions already provided

Plan mode ensures alignment on approach before implementation, preventing wasted effort.

## Patterns and Conventions

### Dependency Management
- Minimize use of third-party packages
- Only add external dependencies when:
  - There is no reasonable alternative to implement the functionality
  - The package is secure, well-maintained, and clearly the best option for the use case
- Prefer built-in language/platform features over external libraries

### Data Structures
**StockPriceResponse Structure:**
- **Required fields**: `symbol` (str) and `currentPrice` (Decimal) - these must always be present
- **Optional fields**: All other fields may be `None` if data is unavailable:
  - `name` (str | None): Company name
  - `currency` (str | None): Currency code
  - `previousClosePrice` (Decimal | None): Previous closing price
  - `openPrice` (Decimal | None): Opening price
  - `dayHigh` (Decimal | None): Day's high price
  - `dayLow` (Decimal | None): Day's low price
  - `fiftyDayAverage` (Decimal | None): 50-day moving average
  - `twoHundredDayAverage` (Decimal | None): 200-day moving average
  - `fiftyTwoWeekHigh` (Decimal | None): 52-week high
  - `fiftyTwoWeekLow` (Decimal | None): 52-week low

**Exception Handling:**
- Throw `StockNotFound` when a stock symbol cannot be found (provider returns None)
- Throw `StockInformationIncomplete` when a stock is found but `currentPrice` is unavailable
- Both exceptions have a `symbol` attribute (not `ticker`)

## Pre-Commit Requirements

Before creating any commit, ensure the following:

1. **Run all tests**: Execute `pytest` to verify all tests pass
2. **Verify test coverage**: Ensure new code is adequately tested
3. **Review changes**: Check that only intended changes are staged
4. **Update documentation**: If adding new features, update relevant docs

**Important**: Never commit code with failing tests. The test suite must pass before any commit.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format: `<type>: <description>`

Common types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
