# Architecture & Code Quality Improvements

> Generated from full codebase review (2026-02-27).
> Covers SOLID principles, hexagonal architecture, and code quality.
> DDD context: `Stock` is the aggregate root — notification generation belongs in the entity.

---

## Critical

### 1. `TriggerStocksNotifications` — god use case
**File:** `application/use_cases/trigger_stocks_notifications.py`
**Violation:** SRP
Orchestrates fetching stocks, setting entry prices, triggering milestone notifications,
triggering target price notifications, deleting fulfilled targets, and persisting stock state.
That's 4–5 responsibilities in one use case.
**Suggestion:** Entry price capture belongs in `TargetPrice.set_entry_price()` (already exists) called
by a dedicated service. The use case should coordinate, not implement.

### 2. `Command.execute() -> str` — ISP violation
**File:** `presentation/console/commands/base.py`
**Violation:** ISP
All commands are forced to return a formatted string, coupling presentation formatting
into the command contract. Commands can't return structured results and formatting
can't be tested independently.
**Suggestion:** Return a structured `CommandResult` (or raw data). Let the menu/caller handle formatting.

### ~~3. `stop_monitor.py` imports from `list_monitors.py`~~ ✓ Resolved
`_get_monitor_processes` moved to `utils.py` as `get_running_monitors()`. Both commands now
import from the shared utility module. Tests relocated accordingly.

### 4. `MonitorStocksScript` — SRP violation
**File:** `presentation/scripts/monitor_stocks.py`
**Violation:** SRP, OCP
One class handles config loading/refresh/writing, target price sync, notification triggering,
timing/scheduling loop, and logging. `_write_config()` removal strategy is also hardcoded (OCP).
**Suggestion:** Extract config refresh into focused collaborators. Separate the run loop
orchestration from config and target price management.

---

## Important

### 5. `NotificationService` — two responsibilities + delay-window logic
**File:** `application/services.py`
**Violation:** SRP
`send_stock_notifications()` and `send_stock_targets_notifications()` are separate concerns
bundled in one service. The delay-window tracking logic adds further complexity.
**Suggestion:** The delay-window tracking logic deserves extraction into a `DelayWindowChecker` helper.

### 6. `CheckReadinessCommand` — SRP + OCP violation
**File:** `presentation/console/commands/check_readiness.py`
**Violation:** SRP, OCP
Checks env vars, checks Telegram connectivity, formats output, and aggregates results —
all in one class with mutable `_all_ready` state. Adding a new check requires modifying `execute()`.
**Suggestion:** A list of `Checker` strategies (each returning pass/fail + message) makes this
open for extension.

### 7. `TargetPriceDTO.to_target_price()` — bidirectional DTO
**File:** `application/dtos.py`
**Violation:** Layering concern
DTOs should carry data from domain outward. `to_target_price()` couples the application
layer back to the domain entity — any change to `TargetPrice` forces DTO changes.
**Suggestion:** Reconstruction from DTO → domain entity could live in a factory or the use case itself.

### 8. Format constants duplicated
**Files:** `presentation/console/menu.py`, `presentation/console/utils.py`
**Violation:** DRY
`"=" * 60` and `"-" * 60` appear in both files.
**Suggestion:** Centralize as named constants in `utils.py`.

### 9. Mutable `list` field in frozen `SymbolConfig`
**File:** `presentation/scripts/config.py`
**Violation:** Correctness risk
`prices: list[Decimal]` in a `frozen=True` dataclass prevents reassignment but not mutation
of the list itself.
**Suggestion:** Use `tuple[Decimal, ...]` instead.

### 10. Missing exception chaining in `ConfigManager`
**File:** `presentation/scripts/config.py`
`raise ConfigLoadingFailed(...)` without `from e` loses the original traceback.
**Suggestion:** Use `raise ConfigLoadingFailed(...) from e`.

### 11. `logging.py` accesses `os.environ` directly
**File:** `infrastructure/logging.py`
Inconsistent with the `SettingsFactory` pattern used elsewhere. Also has unexplained
magic constants (`5 * 1024 * 1024`, `backupCount=3`).
**Suggestion:** Either use `SettingsFactory` or extract constants with explanatory names.

### 12. `YahooFinanceProvider` — SRP violation
**File:** `infrastructure/implementations.py`
**Violation:** SRP
Fetches data, maps market state, builds `Stock` objects (37-line `_build_response`),
and handles errors. The `len(info) <= 3` guard is also unexplained.
**Suggestion:** Extract a `YahooFinanceMapper` responsible for converting raw yfinance
data to domain objects. Document the `<= 3` threshold.

---

## Minor

### 13. `Notification` factory methods — code duplication
**File:** `domain/notifications.py`
20+ near-identical factory methods. Could use a shared internal builder for percentage-based
notifications to reduce boilerplate.

### 14. `Stock` — duplicated SMA detection methods (code quality only)
**File:** `domain/stocks.py`
**Note:** `Stock` as aggregate root generating notifications is valid DDD — this is NOT an SRP
violation in that context. However, the 50-day and 200-day SMA private methods are
near-identical duplicates that could be unified into one parametric method.

### 15. `Stock` — magic threshold constants (code quality only)
**File:** `domain/stocks.py`
`_CLOSE_TO_SMA_UPPER_THRESHOLD` and `_CLOSE_TO_SMA_LOWER_THRESHOLD` are hardcoded.
Consider making them named domain constants or configurable at construction.

### 16. `registry.py` — old-style type hints
**File:** `presentation/console/commands/registry.py`
Uses `Dict[str, Command]` (from `typing`) instead of `dict[str, Command]` (Python 3.9+ built-in).

### 17. `list_monitors.py` — fragile `ps aux` parsing
**File:** `presentation/console/commands/list_monitors.py`
Column index assumptions (`parts[1]`, `parts.index("-m") + 2`) are brittle across Unix variants.
No bounds validation.

### 18. `CommandFactory` — stores unused dependencies
**File:** `presentation/console/factories.py`
`_stock_provider` and `_message_sender` are injected but not used by all commands
(monitor, list, stop don't need them).

### 19. `TelegramMessageSender` — re-raises `HTTPError` unwrapped
**File:** `infrastructure/implementations.py`
Re-raises `urllib.error.HTTPError` without wrapping into a domain-level error, coupling
callers to the HTTP transport.

### 20. Test coverage gaps
- `SettingsFactory` has no tests (env var parsing, defaults, missing vars)
- `TargetPriceDTO` missing round-trip test (`from_target_price` → `to_target_price`)

---

## DDD Context Note

`Stock` is the **aggregate root**. It is correct and expected for it to:
- Hold state (prices, averages, market state)
- Enforce domain invariants
- Emit domain events via `generate_notifications()`

The SRP/OCP flags raised by automated analysis do not apply here — this is standard DDD
aggregate behavior. The only valid concerns for `Stock` are code quality items (#14, #15 above),
not structural ones.

---

## Priority Summary

| Priority | # | Item |
|---|---|---|
| High | 1 | Break up `TriggerStocksNotifications` |
| High | 2 | Fix `Command.execute() -> str` ISP issue |
| ~~High~~ | ~~3~~ | ~~Move `_get_monitor_processes` to `utils.py`~~ ✓ |
| High | 4 | Break up `MonitorStocksScript` responsibilities |
| Medium | 5 | Extract delay-window logic from `NotificationService` |
| Medium | 6 | `CheckReadinessCommand` → Checker strategy pattern |
| Medium | 7 | Remove bidirectional conversion from `TargetPriceDTO` |
| Medium | 8 | Centralize format constants |
| Medium | 9 | `tuple` instead of `list` in `SymbolConfig` |
| Medium | 10 | Add `from e` in `ConfigManager` exception re-raise |
| Medium | 11 | Fix `logging.py` env access + magic constants |
| Medium | 12 | Extract `YahooFinanceMapper` |
| Low | 13–20 | Remaining minor items |
