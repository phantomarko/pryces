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

### Update Documentation After Changes
**IMPORTANT**: Whenever you make significant changes to the codebase (new features, API changes, new fields, renamed parameters, etc.), you MUST update both of the following:

**README.md** (user-facing documentation):
- Update example outputs to match current output format
- Update command examples if CLI arguments change
- Add documentation for new features
- Ensure all examples are accurate and tested

**CLAUDE.md — Architecture Overview** (developer-facing reference):
- Update file/class descriptions when responsibilities change
- Add entries for new files, classes, or exported helpers
- Remove or rename entries when things are deleted or renamed
- Keep the layer descriptions (Domain, Application, Infrastructure, Presentation) accurate

Both must stay synchronized with the actual code behavior.

**Documentation changes must be committed in the same commit as the code they describe** — never in a separate follow-up commit. A commit that changes behavior without updating its documentation is incomplete.

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

**Before editing any file you have not already read in this session, use the Explore agent to navigate to it** — do not guess at file paths or class locations from memory alone.

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

### Always Run and Update Tests After Code Changes
**IMPORTANT**: After making any code changes, you MUST:

1. **Run the full test suite** to verify nothing is broken: `source venv/bin/activate && pytest`
2. **Fix any failing tests** caused by your changes before considering the task done
3. **Add new tests** to cover new behavior — new commands, use cases, services, or non-trivial logic must have corresponding tests
4. **Delete obsolete tests** when removing the code they cover

**Test structure rules:**
- Mirror the `src/` layout under `tests/` — `src/pryces/domain/stocks.py` → `tests/domain/test_stocks.py`
- Use `@pytest.fixture` for shared setup; avoid repeating setup logic across test functions
- Test the public API of each unit, not its internal implementation — if a test breaks on a private rename, the test is wrong
- Prefer many small focused test functions over large tests that check multiple behaviors

Never consider an implementation task complete without a passing test suite.

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
- `stocks.py` — `MarketState` enum (OPEN, PRE, POST, CLOSED), `InstrumentType` enum (STOCK, ETF, CRYPTO, INDEX), `StockSnapshot` frozen dataclass (captures mutable price/market fields), `Stock` entity (symbol, current_price + optional: name, currency, market_state, kind, and 10 Decimal price fields; owns `_targets: list[TargetPrice]` and `_fulfilled_targets: list[TargetPrice]` internally; `update(source)` captures current state as `StockSnapshot` then copies fields from source, preserves accumulated notifications and targets; `is_market_state_transition()` checks snapshot vs current market state; `sync_targets(target_values: list[Decimal])` creates `TargetPrice` internally, matches incoming values vs existing by `.target` — keeps existing (preserves entry price), creates new ones (calls `set_entry_price(self)`), removes targets no longer in incoming list; `generate_notifications() -> None` parameterless, generates notifications into `_pending_notifications` staging list with domain-level deduplication by `NotificationType` across both `_notifications` (historical) and `_pending_notifications` — `TARGET_PRICE_REACHED` is never deduplicated; removes triggered targets from `_targets` and accumulates them in `_fulfilled_targets`; market open/close notifications are skipped for `InstrumentType.CRYPTO` (crypto markets run 24/7), but all other notifications (SMA, 52-week, percentage, targets) are generated normally for crypto without the first-call deferral; when `REGULAR_MARKET_OPEN` is first generated (non-crypto only), all other notifications are deferred to the next call (avoids notification burst on market open); target notifications only generated when market is OPEN; generation order within a market-open cycle matters: SMA50 crossed → close-to-SMA50 → SMA200 crossed → close-to-SMA200 → 52-week high/low → percentage change → session gains/losses erased → target prices; close-to-SMA notifications are suppressed when the corresponding SMA crossing has already been notified (checks both historical and pending); percentage change thresholds are instrument-type-aware with three profiles: STOCK uses 4/8/12/16/20% (`_STOCK_INCREASE_THRESHOLDS`, `_STOCK_DECREASE_THRESHOLDS`), CRYPTO uses 2/4/6/8/10% (`_CRYPTO_INCREASE_THRESHOLDS`, `_CRYPTO_DECREASE_THRESHOLDS`), INDEX/ETF/None use 0.75/1.5/2.25/3/3.75% (`_DEFAULT_INCREASE_THRESHOLDS`, `_DEFAULT_DECREASE_THRESHOLDS`); each threshold maps to a level-based `NotificationType` (LEVEL_1..5); percentage change notifications are always added to `_pending_notifications` during generation; 52-week high/low notifications use the common price-change prefix format with percentage change, require `previous_close_price` to generate; `drain_notifications() -> list[str]` consolidates pending notifications per cycle — classifies each by type as standalone (`_STANDALONE_NOTIFICATION_TYPES`: market open/close, target reached), milestone (`_MILESTONE_NOTIFICATION_TYPES`: SMA crossed/close-to, 52-week high/low, session gains/losses erased), or header-only (percentage change); milestones are merged into a single message with a price-change header line and `-- {message}` bullet lines; when milestones exist, header-only percentage notifications are suppressed from output (implicitly conveyed by the consolidated header) but still moved to historical for deduplication; header-only notifications emit as-is only when no milestones exist; standalone notifications always emit separately; all pending notifications move to historical `_notifications` after drain — follows generate → drain → historical lifecycle; `drain_fulfilled_targets() -> list[Decimal]` returns target values from fulfilled targets and clears the accumulator)
- `notifications.py` — `NotificationType` enum (CLOSE_TO_SMA50, CLOSE_TO_SMA200, SMA50_CROSSED, SMA200_CROSSED, REGULAR_MARKET_OPEN, REGULAR_MARKET_CLOSED, LEVEL_1_INCREASE, LEVEL_2_INCREASE, LEVEL_3_INCREASE, LEVEL_4_INCREASE, LEVEL_5_INCREASE, LEVEL_1_DECREASE, LEVEL_2_DECREASE, LEVEL_3_DECREASE, LEVEL_4_DECREASE, LEVEL_5_DECREASE, SESSION_GAINS_ERASED, SESSION_LOSSES_ERASED, NEW_52_WEEK_HIGH, NEW_52_WEEK_LOW, TARGET_PRICE_REACHED), `Notification` class (factory-based construction with static creators; milestone factories store only the event-specific text as `_message` (e.g., `"crossed SMA50 at 145.00"`, `"hit a new 52-week high"`) — the price-change header is built by `drain_notifications()` during consolidation; standalone factories (market open/close, percentage change, target reached) store the full message; `create_percentage_change(notification_type, symbol, current_price, change_percentage)` single factory for all percentage level notifications)
- `utils.py` — `_calculate_percentage_change(current, reference)` private domain utility (computes `(current - reference) / reference * 100`)
- `target_prices.py` — `TargetPrice` entity (target, entry; `set_entry_price(stock)` captures entry price; `is_reached(stock)` returns bool indicating whether target price has been reached)

**Application** (`src/pryces/application/`) — Use cases, services, and port interfaces:
- `interfaces.py` — all port ABCs: `StockProvider` (get_stocks), `StockRepository` (save_batch, get), `MarketTransitionRepository` (save, get, delete — tracks first-detected market state transition timestamp per symbol), `MessageSender` (send_message), `Logger` (debug, info, warning, error), `LoggerFactory` (get_logger(name) → Logger)
- `dtos.py` — `StockDTO` (maps domain Stock to DTO, includes market_state and kind: str | None), `TargetPriceDTO` (symbol + target Decimal)
- `exceptions.py` — `StockNotFound`
- `services.py` — `DelayWindowChecker` (checks whether a stock is in the post-transition delay window — reads/writes `MarketTransitionRepository`; injectable `clock: Callable[[], datetime]` for testing; `is_in_delay_window(stock) -> bool`), `NotificationService` (sends stock notifications via `MessageSender`; `send_stock_notifications(stock)` delegates suppression decision to injected `DelayWindowChecker`, then calls `stock.generate_notifications()` followed by `stock.drain_notifications()` and sends each message; deduplication is handled at the domain level by `Stock`), `StockSynchronizer` (fetches fresh stocks via `StockProvider`, merges with existing state from `StockRepository` via `Stock.update()`, syncs target prices via `Stock.sync_targets()`, persists via `save_batch`; `fetch_and_sync(symbols, targets) -> list[Stock]`, `persist(stocks)`)
- `use_cases/get_stocks_prices.py` — `GetStocksPrices` (batch symbols → list[StockDTO])
- `use_cases/send_messages.py` — `SendMessages` (sends list of messages → success/failed counts)
- `use_cases/trigger_stocks_notifications.py` — `TriggerStocksNotifications` + `TriggerStocksNotificationsRequest` (symbols + targets: `dict[str, list[Decimal]]`; delegates stock fetching/merging/target-sync to `StockSynchronizer.fetch_and_sync()`, triggers notifications via `NotificationService.send_stock_notifications(stock)`, drains fulfilled targets via `stock.drain_fulfilled_targets()`, persists via `StockSynchronizer.persist()`; `handle()` returns `list[TargetPriceDTO]` of fulfilled targets)

**Infrastructure** (`src/pryces/infrastructure/`) — Adapter implementations:
- `providers.py` — `YahooFinanceSettings` frozen dataclass (max_workers, extra_delay_in_minutes), `YahooFinanceMapper` (converts raw yfinance info dicts to domain `Stock` objects — maps MarketState from yfinance values, maps quoteType to InstrumentType (EQUITY→STOCK, ETF→ETF, CRYPTOCURRENCY→CRYPTO, INDEX→INDEX; unknown types map to None), handles price fallback chain, adds `extra_delay_in_minutes` to yfinance-reported delay unconditionally; injects `logger_factory: LoggerFactory`), `YahooFinanceProvider` implements `StockProvider` via `yfinance` (delegates mapping to `YahooFinanceMapper`; `_get_stock` handles all yfinance exceptions internally — logs and returns `None` on failure; injects `logger_factory: LoggerFactory`)
- `senders.py` — `TelegramSettings` frozen dataclass (bot_token, group_id), `TelegramMessageSender` implements `MessageSender` via Telegram Bot API (raises `MessageSendingFailed` on all failure paths: HTTP errors with `retryable=True` for 429/5xx, network errors with `retryable=True`, `ok=false` responses with `retryable=False`; injects `logger_factory: LoggerFactory`), `RetrySettings` frozen dataclass (max_retries, base_delay, backoff_factor), `RetryMessageSender` decorator implementing `MessageSender` (wraps any `MessageSender`; retries on `MessageSendingFailed` with `retryable=True` using exponential backoff; raises immediately on non-retryable failures or when max_retries exceeded; injects `logger_factory: LoggerFactory`), `FireAndForgetMessageSender` decorator implementing `MessageSender` (wraps any `MessageSender`; submits calls to a single-worker `ThreadPoolExecutor` and returns `True` immediately; logs exceptions from the inner sender; `shutdown()` waits for pending messages — used in monitor script only; injects `logger_factory: LoggerFactory`)
- `receivers.py` — `BotUpdate` frozen dataclass (update_id, chat_id, text), `TelegramUpdatePoller` (long-polls Telegram `getUpdates` API with `timeout=30`; returns `list[BotUpdate]`; skips updates without text; returns `[]` on any HTTP/network error; injects `logger_factory: LoggerFactory`)
- `repositories.py` — `InMemoryMarketTransitionRepository` implements `MarketTransitionRepository` (in-memory dict store), `InMemoryStockRepository` implements `StockRepository` (in-memory dict store)
- `exceptions.py` — `ConfigurationError` (raised by `SettingsFactory` on missing or invalid env vars)
- `factories.py` — `SettingsFactory` (creates `YahooFinanceSettings` from `MAX_FETCH_WORKERS` env var and optional `extra_delay_in_minutes: int = 0` parameter (no longer from env), creates `TelegramSettings` from Telegram env vars, creates `LoggingSettings` for cli/monitor/bot entry points; raises `ConfigurationError` on missing vars or non-integer `MAX_FETCH_WORKERS`)
- `logging.py` — `CLI_ENTRY_POINT`, `MONITOR_ENTRY_POINT`, `BOT_ENTRY_POINT` constants; `LoggingSettings` frozen dataclass; `setup_logging(settings)` configures root logger per entry point: stderr handler if verbose, file handler (named `pryces_{entry_point}_timestamp.log`) if `LOGS_DIRECTORY` is set, `NullHandler` fallback if no handlers; `debug` scopes DEBUG level to `pryces` logger only; `PythonLogger` implements `Logger` (wraps `logging.Logger`, delegates all level calls); `PythonLoggerFactory` implements `LoggerFactory` (delegates to `logging.getLogger(name)`) — instantiated once at each composition root

**Presentation** (`src/pryces/presentation/console/`) — Interactive CLI:
- `cli.py` — Entry point, composition root (wires dependencies)
- `menu.py` — `InteractiveMenu` (main loop, I/O via injectable streams)
- `commands/base.py` — `Command` ABC, `CommandMetadata`, `InputPrompt` (frozen dataclass: `key`, `prompt`, optional `validator`, optional `preamble: str | None` — displayed before the prompt by the menu), `CommandResult` (frozen dataclass: `message: str`, `success: bool = True`)
- `commands/get_stocks_prices.py` — `GetStocksPricesCommand` (one or multiple symbols → formatted output; injects `logger_factory: LoggerFactory`)
- `commands/list_configs.py` — `ListConfigsCommand` (scans `CONFIGS_DIR` via `get_config_files()`, loads each config via `ConfigManager`, displays interval + symbols per config)
- `commands/create_config.py` — `CreateConfigCommand` (prompts for name, interval, symbols with optional target prices; creates config JSON in `CONFIGS_DIR`; name validator ensures no `/` or `.`, no duplicates)
- `commands/edit_config.py` — `EditConfigCommand` (dynamic prompts: config picker → operation (1=interval, 2=symbols) → new value; lenient prompt-time validator, strict parse in `execute()`; returns `success=False` on bad input)
- `commands/delete_config.py` — `DeleteConfigCommand` (dynamic prompts: config picker → confirm "yes"/"no"; deletes via `Path.unlink()`)
- `commands/monitor_stocks.py` — `MonitorStocksCommand` (dynamic config picker from `CONFIGS_DIR` via `get_config_files()`; prompts for duration and extra delay; launches the standalone monitor script as a detached background process via `subprocess.Popen`, returns PID; returns error if no configs found)
- `commands/list_monitors.py` — `ListMonitorsCommand` (queries `ps aux` for running monitor script processes, extracts PID and config path; displays numbered entries)
- `commands/stop_monitor.py` — `StopMonitorCommand` (uses standard `Command` contract: `get_input_prompts()` fetches running monitors and returns an `InputPrompt` with preamble showing the process list and a selection validator; `execute()` kills the selected process or returns cancellation/no-processes message)
- `commands/check_readiness.py` — `CheckResult` frozen dataclass (`ready: bool`, `message: str`), `Checker` ABC (`check() -> CheckResult`), `EnvVarsChecker` (validates all env vars), `TelegramChecker` (sends test message; injects `SendMessages` + `Logger`), `CheckReadinessCommand` (orchestrates a `list[Checker]`; iterates checkers, aggregates results, appends warning on any failure; injects `logger_factory: LoggerFactory`)
- `commands/registry.py` — `CommandRegistry` (registry pattern)
- `factories.py` — `CommandFactory` (DI + object creation; injects `logger_factory: LoggerFactory`, threads it to commands that need it)
- `utils.py` — `CONFIGS_DIR: Path` (project root `configs/` directory); shared validators (`validate_symbol`, `validate_symbols`, `validate_positive_integer`, `validate_non_negative_integer`, `validate_file_path`, `validate_symbols_with_targets`, `create_monitor_selection_validator(process_count) -> Callable`, `create_config_selection_validator(count) -> Callable`); parsers (`parse_symbols_input`, `parse_symbols_with_targets`); formatters (`format_stock`, `format_stock_list`, `format_running_monitors`, `format_config_list`, `format_config_details`); `get_running_monitors() -> list[tuple[str, str]]` (queries `ps -eo pid=,cmd=`); `get_config_files() -> list[Path]` (returns sorted `*.json` from `CONFIGS_DIR`)

**Presentation — Scripts** (`src/pryces/presentation/scripts/`) — Standalone scripts for automated execution:
- `config.py` — `CONFIGS_DIR: Path` (project root `configs/` directory); `SymbolConfig` frozen dataclass (symbol, prices as `list[Decimal]` — no validation), `MonitorStocksConfig` frozen dataclass (interval, symbols as `list[SymbolConfig]` — with validation), `ConfigManager` (loads/writes JSON config file, raises `ConfigLoadingFailed` on any error), `ConfigRefresher` (owns config lifecycle: `refresh()` hot-reloads config from disk via `ConfigManager`, `remove_fulfilled_targets(fulfilled)` filters out fulfilled `TargetPriceDTO` prices from config symbols — keeping the symbol entry even when all its prices are removed — and persists via `ConfigManager.write_monitor_stocks_config`, `log_config()` logs monitoring cadence and symbols; holds mutable `config` property; injects `logger_factory: LoggerFactory`); `find_config_for_symbol(symbol) -> tuple[Path, MonitorStocksConfig] | None` (scans `CONFIGS_DIR` alphabetically, returns first config containing the symbol); `find_config_by_name(config_name) -> tuple[Path, MonitorStocksConfig] | None` (looks up config by name, returns None if not found or load fails); `get_all_tracked_symbols() -> list[str]` (scans all configs, collects unique symbols, returns sorted list); `get_config_names() -> list[str]` (returns sorted list of config file stems from `CONFIGS_DIR`, no file content read)
- `exceptions.py` — `ConfigLoadingFailed`
- `bot_commands.py` — `_MAX_MESSAGE_LENGTH` (256), `_MAX_INTEGER_DIGITS` (7), `_MAX_DECIMAL_DIGITS` (8) module-level constants; `_validate_price(raw) -> Decimal | str` (string-based validation before `Decimal()` conversion — rejects negative/zero values, scientific notation, and oversized digit strings; returns `"Invalid price"` on failure); `BotCommand` ABC (name, usage, description, arg_count, execute), `TargetsCommand` (lists target prices for a symbol), `TargetAddCommand` (adds a target price to a symbol's config; uses `_validate_price`), `TargetRemoveCommand` (removes a target price from a symbol's config; uses `_validate_price`), `SymbolAddCommand` (adds a new symbol entry to a named config; injects `_FindConfigByNameFn`), `SymbolRemoveCommand` (removes a symbol from whichever config contains it; guards against removing the last symbol; injects `_FindConfigFn`), `SymbolsCommand` (lists all tracked symbols across configs; injects `_GetAllSymbolsFn`), `ConfigsCommand` (lists all config file names without path or extension; injects `_GetConfigNamesFn`), `HelpCommand` (formats usage for all commands); `_FindConfigFn`, `_FindConfigByNameFn`, `_GetAllSymbolsFn`, `_GetConfigNamesFn` type aliases; `_find_symbol_config`, `_update_symbol_prices`, `_add_symbol_to_config`, `_remove_symbol_from_config` private helpers shared by command implementations; `BotCommandDispatcher` (routes text to commands by name, silently ignores messages exceeding `_MAX_MESSAGE_LENGTH`, returns empty string for non-commands, error message for unknown commands or wrong arg count; injects `logger_factory: LoggerFactory`, logs command name and args on execution)
- `monitor_stocks.py` — Standalone monitor script (`MonitorStocksScript` class, argparse CLI, logging). Entry point: `main()`. Args: `config` (required path), `--duration` (int, required — monitoring duration in minutes), `--extra-delay` (int, default 0 — passed to `SettingsFactory.create_yahoo_finance_settings()`), `--debug`, `--verbose`. Single responsibility: orchestrating the monitoring cycle (loop, scheduling, delegation). Delegates config lifecycle to injected `ConfigRefresher`, passes target prices from config into `TriggerStocksNotificationsRequest.targets` on each iteration. Composition root (`_create_script`) creates a single `PythonLoggerFactory` instance and threads it to all infrastructure adapters, `ConfigRefresher`, and `MonitorStocksScript`; `_ScriptContext` groups the script and sender so `main()` calls `shutdown()` in a `finally` block. `MonitorStocksScript` injects `logger_factory: LoggerFactory`.
- `telegram_bot.py` — Standalone Telegram bot script (`TelegramBotScript` class, argparse CLI). Entry point: `main()`. Args: `--debug`, `--verbose`. Long-polls Telegram for commands, filters by `TELEGRAM_GROUP_ID`, dispatches to `BotCommandDispatcher`, sends replies via `TelegramMessageSender`. Composition root (`_create_script`) wires `TelegramUpdatePoller`, `TelegramMessageSender`, bot commands, and dispatcher.

### Key Patterns
- **Ports & Adapters**: Application defines ABCs, infrastructure implements them
- **Command Pattern**: Each CLI action is a `Command` with metadata, input prompts, and execute
- **Factory + Registry**: `CommandFactory` builds commands, `CommandRegistry` stores them
- **Dependency Injection**: Wired at composition root in `cli.py`

### Entry Points
```bash
python -m pryces.presentation.console.cli                         # Interactive CLI
python -m pryces.presentation.scripts.monitor_stocks CONFIG_PATH --duration N  # Monitor script
python -m pryces.presentation.scripts.telegram_bot                # Telegram bot for target management
```

## Patterns and Conventions

### Dependency Management
- Minimize use of third-party packages
- Only add external dependencies when:
  - There is no reasonable alternative to implement the functionality
  - The package is secure, well-maintained, and clearly the best option for the use case
- Prefer built-in language/platform features over external libraries

### PEP 8 Compliance

All Python code must follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines:
- **Line length**: Maximum 100 characters (enforced by `black`)
- **Naming**: `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants, `_prefix` for private members
- **Imports**: Standard library → third-party → local; one import per line; no wildcard imports
- **Type hints**: Use built-in generics (`dict`, `list`, `tuple`) over `typing` equivalents (`Dict`, `List`, `Tuple`) — requires Python 3.9+
- **Formatting**: Enforced automatically by the `black` pre-commit hook — never skip it
- **No shadowing built-ins**: Never use built-in names (`type`, `id`, `list`, `dict`, `filter`, etc.) as parameter or variable names — rename to something more specific (e.g. `notification_type` instead of `type`)

### Class Member Ordering

Within every class, members must appear in this order:
1. `__slots__`
2. Class-level constants and attributes
3. `__init__` (then other dunder/magic methods if any)
4. Properties (`@property`)
5. Public instance methods
6. Private/protected methods (`_` prefix)

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

**Commit rules (non-negotiable):**
- **Tests must pass before every commit** — never commit with a failing test suite
- **Never skip pre-commit hooks** (`--no-verify` is forbidden unless the user explicitly instructs it; if a hook fails, fix the root cause)
- **Atomic commits** — one logical change per commit; do not mix unrelated changes
- **Documentation in the same commit** — if the commit changes behavior, CLAUDE.md and/or README.md must be updated in that same commit, not a follow-up
