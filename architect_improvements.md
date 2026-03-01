# Architecture & Code Quality Improvements

## Purpose & Origin

This document tracks **deliberate, prioritized architectural improvements** to the Pryces codebase.
It is a living backlog — not a static report. Each item records a specific design violation, its
rationale, and the recommended fix. Items are marked resolved when the code actually reflects the fix.

**Why it exists:** Pryces is built on SOLID principles, hexagonal (Ports & Adapters) architecture,
and DDD. As the codebase evolves, violations accumulate incrementally — a single class gains one
extra responsibility, a DTO grows a reverse method, an abstraction leaks. This document captures
those violations as they are identified so they can be addressed intentionally rather than
discovered accidentally during future changes.

**How to use it:**
- Before starting an architectural task, read the relevant item for full context and the suggested fix.
- After resolving an item, strike it through with `~~` and add `✓ Resolved` plus a brief note.
- Add new items as violations are discovered — include the file, the principle violated, and a
  concrete suggestion.
- Do not delete resolved items; they serve as a record of intentional design decisions.

**Design constraints all items are evaluated against:**
- **SRP** — one reason to change per class/module
- **OCP** — extend by adding, not by modifying
- **LSP** — implementations interchangeable through port interfaces
- **ISP** — port interfaces focused and minimal
- **DIP** — depend on abstractions, not concretions
- **Hexagonal architecture** — domain and application layers never depend on infrastructure or
  presentation; dependencies always point inward
- **DDD** — `Stock` is the aggregate root; owning state, enforcing invariants, and emitting
  domain events via `generate_notifications()` is correct aggregate behavior, not an SRP violation

> Generated from full codebase review (2026-02-27). Last audited: 2026-03-01.

---

## Critical

### ~~1. `TriggerStocksNotifications` — god use case~~ ✓ Resolved
Stock state management (fetch, merge, sync targets, persist) extracted into `StockSynchronizer`
application service. The use case now coordinates two collaborators: `StockSynchronizer` and
`NotificationService`.

### ~~2. `Command.execute() -> str` — ISP violation~~ ✓ Resolved
`CommandResult(message: str, success: bool = True)` introduced in `base.py`. All commands
return `CommandResult`; `menu.py` reads `result.message`. Error paths set `success=False`.

### ~~3. `stop_monitor.py` imports from `list_monitors.py`~~ ✓ Resolved
`_get_monitor_processes` moved to `utils.py` as `get_running_monitors()`. Both commands now
import from the shared utility module. Tests relocated accordingly.

### ~~4. `MonitorStocksScript` — SRP violation~~ ✓ Resolved
Config lifecycle (hot-reload, write-back, logging) extracted into `ConfigRefresher` collaborator
in `config.py`. `MonitorStocksScript` now has a single responsibility: orchestrating the
monitoring cycle.

---

## Important

### ~~5. `NotificationService` — delay-window logic not extracted~~ ✓ Resolved
`DelayWindowChecker` extracted into a dedicated collaborator in `services.py`. It owns
`MarketTransitionRepository` + `clock` and exposes `is_in_delay_window(stock) -> bool`.
`NotificationService` now accepts `DelayWindowChecker` and has a single responsibility: deciding
whether to send and forwarding messages.

### 6. `CheckReadinessCommand` — SRP + OCP violation
**File:** `presentation/console/commands/check_readiness.py`
**Violation:** SRP, OCP
Checks env vars, checks Telegram connectivity, formats output, and aggregates results —
all in one class with mutable `_all_ready` state. Adding a new check requires modifying `execute()`.
**Suggestion:** A list of `Checker` strategies (each returning pass/fail + message) makes this
open for extension.

### ~~7. `TargetPriceDTO.to_target_price()` — bidirectional DTO~~ ✓ Resolved
`TargetPriceDTO` is now a simple data container with no `to_target_price()` method.
Reconstruction from DTO → domain entity happens in `TriggerStocksNotifications.handle()` by
passing raw `Decimal` values to `Stock.sync_targets()`, removing the DTO-to-domain coupling.

### ~~8. Format constants duplicated~~ ✓ Resolved
`SEPARATOR = "-" * 60` and `DOUBLE_SEPARATOR = "=" * 60` are centralized in `utils.py` and
reused through formatting functions. Duplication eliminated.

### 9. Mutable `list` field in frozen `SymbolConfig`
**File:** `presentation/scripts/config.py`
**Violation:** Correctness risk
`prices: list[Decimal]` in a `frozen=True` dataclass prevents reassignment but not mutation
of the list itself.
**Suggestion:** Use `tuple[Decimal, ...]` instead.

### 10. Missing exception chaining in `ConfigManager`
**File:** `presentation/scripts/config.py`
All three `raise ConfigLoadingFailed(...)` branches lack `from e`, losing the original traceback
for `FileNotFoundError`, `json.JSONDecodeError`/`TypeError`/`ValueError`/`KeyError`, and the
catch-all `Exception`.
**Suggestion:** Use `raise ConfigLoadingFailed(...) from e` in every branch.

### 11. `logging.py` accesses `os.environ` directly
**File:** `infrastructure/logging.py`
Inconsistent with the `SettingsFactory` pattern used elsewhere. Also has unexplained
magic constants (`5 * 1024 * 1024`, `backupCount=3`).
**Suggestion:** Either use `SettingsFactory` or extract constants with explanatory names.

### ~~12. `YahooFinanceProvider` — SRP violation~~ ✓ Resolved
`YahooFinanceMapper` extracted into a separate class responsible for converting raw yfinance
data to domain `Stock` objects. `YahooFinanceProvider` now delegates mapping to the
`YahooFinanceMapper`, maintaining focus on data fetching. The `len(info) <= 3` threshold
is documented as a guard against incomplete API responses.

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

### ~~16. `registry.py` — old-style type hints~~ ✓ Resolved
`CommandRegistry` now uses `dict[str, Command]` (Python 3.9+ built-in generic) correctly.

### 17. `utils.py` — fragile `ps aux` parsing
**File:** `presentation/console/utils.py` (previously `list_monitors.py`)
Column index assumptions (`parts[1]`, `parts.index("-m") + 2`) in `get_running_monitors()` are
brittle across Unix variants. While a bounds check (`if module_index < len(parts)`) exists,
there is no validation that `parts[1]` is a valid PID.
**Suggestion:** Use `ps` with explicit `-o` format specifier for reliable column extraction.

### ~~18. `CommandFactory` — stores unused dependencies~~ ✓ Resolved
`_stock_provider` is used by `GetStocksPricesCommand` and `_message_sender` is used by
`CheckReadinessCommand`. Both dependencies are consumed by at least one command each.

### 19. `TelegramMessageSender` — re-raises `HTTPError` unwrapped
**File:** `infrastructure/senders.py`
Re-raises `urllib.error.HTTPError` without wrapping into a domain-level error, coupling
callers to the HTTP transport.
**Suggestion:** Catch and wrap in a custom infrastructure exception before re-raising.

### 20. Test coverage gaps
- `SettingsFactory` has no tests (env var parsing, defaults, missing vars, invalid integers)

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
| ~~High~~ | ~~1~~ | ~~Break up `TriggerStocksNotifications`~~ ✓ |
| ~~High~~ | ~~2~~ | ~~Fix `Command.execute() -> str` ISP issue~~ ✓ |
| ~~High~~ | ~~3~~ | ~~Move `_get_monitor_processes` to `utils.py`~~ ✓ |
| ~~High~~ | ~~4~~ | ~~Break up `MonitorStocksScript` responsibilities~~ ✓ |
| ~~Medium~~ | ~~5~~ | ~~Extract `DelayWindowChecker` from `NotificationService`~~ ✓ |
| Medium | 6 | `CheckReadinessCommand` → Checker strategy pattern |
| ~~Medium~~ | ~~7~~ | ~~Remove bidirectional conversion from `TargetPriceDTO`~~ ✓ |
| ~~Medium~~ | ~~8~~ | ~~Centralize format constants~~ ✓ |
| Medium | 9 | `tuple` instead of `list` in `SymbolConfig` |
| Medium | 10 | Add `from e` in `ConfigManager` exception re-raise (all 3 branches) |
| Medium | 11 | Fix `logging.py` env access + magic constants |
| ~~Medium~~ | ~~12~~ | ~~Extract `YahooFinanceMapper`~~ ✓ |
| ~~Low~~ | ~~16~~ | ~~Fix old-style type hints in `registry.py`~~ ✓ |
| ~~Low~~ | ~~18~~ | ~~`CommandFactory` stores unused dependencies~~ ✓ |
| Low | 13–15, 17, 19–20 | Remaining minor items |
