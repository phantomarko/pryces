# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pryces is a Python project built with clean architecture principles, emphasizing SOLID design, minimal dependencies, and clear separation of concerns.

## Design Principles

All code must follow **SOLID principles**, **hexagonal architecture**, and **clean code** practices:
- **Single Responsibility**: Each class/module has one reason to change
- **Open/Closed**: Extend behavior through new implementations, not modifying existing code
- **Liskov Substitution**: Implementations must be interchangeable through their port interfaces
- **Interface Segregation**: Keep port interfaces focused and minimal
- **Dependency Inversion**: Depend on abstractions (ports), not concretions (adapters)
- **Hexagonal Architecture**: Domain and application layers never depend on infrastructure or presentation; dependencies always point inward
- **Clean Code**: Meaningful names, small focused functions, no duplication, self-documenting structure

## Critical Directives

### Update README.md After Changes
**IMPORTANT**: Whenever you make significant changes to the codebase (new features, API changes, new fields, renamed parameters, etc.), you MUST update the README.md to reflect these changes:
- Update example outputs to match current output format
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

### Always Use Virtual Environment for Testing
**IMPORTANT**: This project uses a Python virtual environment. You MUST activate it before running any tests or testing code manually.

**Required workflow:**
1. **Before testing**: Activate the virtual environment with `source venv/bin/activate` (or `source .venv/bin/activate` depending on the venv location)
2. **Run tests**: Execute `pytest` or test the CLI manually
3. **After testing**: Deactivate with `deactivate`

**Why this matters:**
- Running tests without the venv will fail due to missing dependencies
- Attempting to install packages globally wastes time and may cause permission errors
- Always check for the venv before running Python commands

**Never**: Try to install the Python environment from scratch or install packages globally. The virtual environment already exists and contains all required dependencies.

## Architecture Overview

Pryces is a stock price CLI tool using **Ports & Adapters** (hexagonal) architecture. External dependencies: `yfinance`, `python-dotenv`.

### Layers

```
Presentation → Application → Domain
                   ↑
            Infrastructure (implements application ports)
```

**Domain** (`src/pryces/domain/`) — Core domain model:
- `stocks.py` — `MarketState` enum (OPEN, PRE, POST, CLOSED), `Stock` entity (symbol, currentPrice + optional: name, currency, marketState, and 10 Decimal price fields; generates milestone notifications via `generate_notifications()`)
- `notifications.py` — `NotificationType` enum (CLOSE_TO_SMA50, CLOSE_TO_SMA200, SMA50_CROSSED, SMA200_CROSSED, REGULAR_MARKET_OPEN, REGULAR_MARKET_CLOSED, plus percentage thresholds), `Notification` class (factory-based construction with static creators)

**Application** (`src/pryces/application/`) — Use cases, services, and port interfaces:
- `interfaces.py` — `StockProvider` ABC (port), `MessageSender` ABC (port)
- `dtos.py` — `StockDTO` (maps domain Stock to DTO, includes marketState)
- `exceptions.py` — `StockNotFound`
- `services.py` — `NotificationService` (sends stock milestone notifications via MessageSender, tracks already-sent per symbol to avoid duplicates)
- `use_cases/get_stock_price.py` — `GetStockPrice` (single symbol → StockDTO)
- `use_cases/get_stocks_prices.py` — `GetStocksPrices` (batch symbols → list[StockDTO])
- `use_cases/send_messages.py` — `SendMessages` (sends list of messages → success/failed counts)
- `use_cases/trigger_stocks_notifications.py` — `TriggerStocksNotifications` (fetches stocks, triggers notifications via NotificationService)

**Infrastructure** (`src/pryces/infrastructure/`) — Adapter implementations:
- `implementations.py` — `YahooFinanceSettings` frozen dataclass (max_workers), `TelegramSettings` frozen dataclass (bot_token, group_id), `YahooFinanceProvider` implements `StockProvider` via `yfinance` (maps MarketState from yfinance values), `TelegramMessageSender` implements `MessageSender` via Telegram Bot API
- `factories.py` — `SettingsFactory` (creates `YahooFinanceSettings` from `MAX_FETCH_WORKERS` env var, creates `TelegramSettings` from Telegram env vars)
- `logging.py` — `setup(verbose, debug)` configures root logger: stderr handler if verbose, file handler if `LOGS_DIRECTORY` is set, `NullHandler` fallback if no handlers; `debug` scopes DEBUG level to `pryces` logger only

**Presentation** (`src/pryces/presentation/console/`) — Interactive CLI:
- `cli.py` — Entry point, composition root (wires dependencies)
- `menu.py` — `InteractiveMenu` (main loop, I/O via injectable streams)
- `commands/base.py` — `Command` ABC, `CommandMetadata`, `InputPrompt`
- `commands/get_stock_price.py` — `GetStockPriceCommand`
- `commands/get_stocks_prices.py` — `GetStocksPricesCommand`
- `commands/monitor_stocks.py` — `MonitorStocksCommand` (launches the standalone monitor script as a detached background process via `subprocess.Popen`, returns PID)
- `commands/check_readiness.py` — `CheckReadinessCommand` (verifies env vars and Telegram connectivity; tracks `_all_ready` state and appends warning on failures)
- `commands/registry.py` — `CommandRegistry` (registry pattern)
- `factories.py` — `CommandFactory` (DI + object creation)
- `utils.py` — Shared validators (`validate_symbol`, `validate_symbols`, `validate_positive_integer`, `validate_file_path`), parsers (`parse_symbols_input`), and formatters (`format_stock`, `format_stock_list`)

**Presentation — Scripts** (`src/pryces/presentation/scripts/`) — Standalone scripts for automated execution:
- `monitor_stocks.py` — Standalone monitor script driven by JSON config (`MonitorStocksConfig` dataclass, `MonitorStocksScript` class, argparse CLI, logging). Entry point: `main()`

### Key Patterns
- **Ports & Adapters**: Application defines ABCs, infrastructure implements them
- **Command Pattern**: Each CLI action is a `Command` with metadata, input prompts, and execute
- **Factory + Registry**: `CommandFactory` builds commands, `CommandRegistry` stores them
- **Dependency Injection**: Wired at composition root in `cli.py`

### Entry Points
```bash
python -m pryces.presentation.console.cli                         # Interactive CLI
python -m pryces.presentation.scripts.monitor_stocks CONFIG_PATH  # Monitor script
```

## Patterns and Conventions

### Dependency Management
- Minimize use of third-party packages
- Only add external dependencies when:
  - There is no reasonable alternative to implement the functionality
  - The package is secure, well-maintained, and clearly the best option for the use case
- Prefer built-in language/platform features over external libraries

### Code Comments

**Write self-documenting code.** Use clear names, structure, and type hints. Only add comments when they explain WHY, not WHAT.

**Rules:**
1. **Type hints eliminate documentation**: If a parameter has a type hint, don't document its type in a docstring
2. **Method names should be obvious**: `get_command()`, `register()`, `validate_symbol()` need no docstring
3. **No restating**: `def __init__()` → "Initialize X" adds zero value
4. **Comments explain reasoning**: Use them for business logic, heuristics, or non-obvious constraints

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format: `<type>: <description>`

Common types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
