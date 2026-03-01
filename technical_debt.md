# Technical Debt

## Overview

This is the **technical debt backlog** for the Pryces codebase. Each item records a specific
design violation, its rationale, and the recommended fix. Resolved items are removed.

Pryces is built on SOLID principles, hexagonal (Ports & Adapters) architecture, and DDD. As the
codebase evolves, violations accumulate incrementally. This document captures them as they are
identified so they can be addressed intentionally rather than discovered accidentally.

**How to use it:**
- Before starting a task, read the relevant item for full context and the suggested fix.
- After resolving an item, remove it from the backlog.
- Add new items as violations are discovered — include the file, the principle violated, and a
  concrete suggestion.

**Design constraints:**
- **SRP** — one reason to change per class/module
- **OCP** — extend by adding, not by modifying
- **LSP** — implementations interchangeable through port interfaces
- **ISP** — port interfaces focused and minimal
- **DIP** — depend on abstractions, not concretions
- **Hexagonal architecture** — domain and application layers never depend on infrastructure or
  presentation; dependencies always point inward
- **DDD** — `Stock` is the aggregate root; owning state, enforcing invariants, and emitting
  domain events via `generate_notifications()` is correct aggregate behavior, not an SRP violation

> Last audited: 2026-03-01.

---

## Important

### 1. `CheckReadinessCommand` — SRP + OCP violation
**File:** `presentation/console/commands/check_readiness.py`
**Violation:** SRP, OCP
Checks env vars, checks Telegram connectivity, formats output, and aggregates results —
all in one class with mutable `_all_ready` state. Adding a new check requires modifying `execute()`.
**Suggestion:** A list of `Checker` strategies (each returning pass/fail + message) makes this
open for extension.

### 2. Mutable `list` field in frozen `SymbolConfig`
**File:** `presentation/scripts/config.py`
**Violation:** Correctness risk
`prices: list[Decimal]` in a `frozen=True` dataclass prevents reassignment but not mutation
of the list itself.
**Suggestion:** Use `tuple[Decimal, ...]` instead.

### 3. Missing exception chaining in `ConfigManager`
**File:** `presentation/scripts/config.py`
All three `raise ConfigLoadingFailed(...)` branches lack `from e`, losing the original traceback
for `FileNotFoundError`, `json.JSONDecodeError`/`TypeError`/`ValueError`/`KeyError`, and the
catch-all `Exception`.
**Suggestion:** Use `raise ConfigLoadingFailed(...) from e` in every branch.

### 4. `logging.py` accesses `os.environ` directly
**File:** `infrastructure/logging.py`
Inconsistent with the `SettingsFactory` pattern used elsewhere. Also has unexplained
magic constants (`5 * 1024 * 1024`, `backupCount=3`).
**Suggestion:** Either use `SettingsFactory` or extract constants with explanatory names.

### 7. `NotificationService` ignores send failures
**File:** `application/services.py`
**Violation:** Clean Code
`send_stock_notifications` calls `self._message_sender.send_message(message)` but ignores the
`bool` return value. Failed sends are completely silent — no logging, no error propagation.
Compare with `SendMessages` use case which properly tracks success/failure counts.
**Suggestion:** At minimum, log failed sends so operational issues are observable.

### 8. Dead exception classes — incomplete error-handling strategy
**File:** `application/exceptions.py`
**Violation:** Clean Code (dead code)
`StockNotFound` and `MessageSendingFailed` are defined but never raised or caught anywhere.
Ports use `None`-returns and `bool`-returns instead. This is inconsistent — the exceptions exist
for a purpose but the interfaces use a different error signaling mechanism.
**Suggestion:** Either wire the exceptions into the ports/use cases (preferred) or remove them.

### 9. `FireAndForgetMessageSender` violates LSP
**File:** `infrastructure/senders.py`
**Violation:** LSP
Always returns `True` regardless of whether the message will actually be sent. Callers relying
on the return value (e.g., `SendMessages` use case) get incorrect results. The two
`MessageSender` implementations are not interchangeable.
**Suggestion:** Document in the port interface that `True` means "accepted for delivery" (not
"delivered"), so both implementations share the same postcondition.

### 10. `TelegramMessageSender` — inconsistent error handling + leaking infra exceptions
**File:** `infrastructure/senders.py`
**Violation:** DIP, Consistency
Two different failure modes: raises `MessageSendingFailed` on HTTP errors but returns `False`
on API logical failures (`ok=false`). Also only catches `HTTPError` — `URLError` (DNS, timeout,
connection refused) propagates as raw urllib exceptions, leaking infrastructure details to the
application layer.
**Suggestion:** Raise `MessageSendingFailed` in all failure cases. Catch `URLError` and `OSError`
too, wrapping with `from e` chaining. Keep `HTTPError` first (it's a subclass of `URLError`).

### 11. `YahooFinanceProvider` — inconsistent exception handling between public methods
**File:** `infrastructure/providers.py`
**Violation:** LSP, Consistency
`get_stock` (public port method) propagates raw yfinance exceptions. `get_stocks` wraps them
via `_fetch_stock` which catches all exceptions and returns `None`. The two port methods have
different failure semantics.
**Suggestion:** Move exception handling into `get_stock` so both code paths behave consistently.

### 12. `SettingsFactory` — misleading exception type + missing validation
**File:** `infrastructure/factories.py`
**Violation:** Robustness, Clean Code
Raises `EnvironmentError` (a built-in alias for `OSError`) for missing env vars — semantically
wrong. Also doesn't catch `ValueError` when `MAX_FETCH_WORKERS` or `EXTRA_DELAY_IN_MINUTES`
contain non-numeric strings.
**Suggestion:** Define a custom `ConfigurationError` exception. Catch `ValueError` alongside
`KeyError` with a clear message including the variable name and value.

### 13. Duplicated process listing format in `StopMonitorCommand` and `ListMonitorsCommand`
**Files:** `presentation/console/commands/stop_monitor.py`, `list_monitors.py`
**Violation:** DRY
Identical header + entry formatting code for listing monitor processes.
**Suggestion:** Extract a `format_running_monitors(processes)` function into `utils.py`.

### 14. `StopMonitorCommand` bypasses the Command I/O contract
**File:** `presentation/console/commands/stop_monitor.py`
**Violation:** LSP
Returns an empty `get_input_prompts()` and does its own interactive I/O inside `execute()` via
injected streams. Every other `Command` delegates I/O to `InteractiveMenu`. Not substitutable
in contexts that rely on the standard input-collection contract.
**Suggestion:** Refactor the two-phase interaction (list + select) into the standard `Command`
contract, with the process selection as an `InputPrompt`.

### 15. `ConfigManager.write_monitor_stocks_config` loses Decimal precision
**File:** `presentation/scripts/config.py`
**Violation:** Correctness risk
`float(p)` conversion when writing prices to JSON can introduce floating-point errors.
On re-read via `Decimal(str(p))`, the imprecise float-stringified value is preserved.
**Suggestion:** Use `str(p)` instead of `float(p)` when serializing to JSON.

### 16. `ConfigRefresher.refresh()` silently swallows all exceptions
**File:** `presentation/scripts/config.py`
**Violation:** Clean Code
Bare `except Exception: pass` with zero logging. If the config file becomes invalid during
monitoring, the operator gets no feedback.
**Suggestion:** Log at WARNING level (e.g., `self._logger.warning(f"Config refresh failed: {e}")`)
so issues are diagnosable while the monitor continues with the last valid config.

---

## Minor

### 5. `utils.py` — fragile `ps aux` parsing
**File:** `presentation/console/utils.py`
Column index assumptions (`parts[1]`, `parts.index("-m") + 2`) in `get_running_monitors()` are
brittle across Unix variants. While a bounds check (`if module_index < len(parts)`) exists,
there is no validation that `parts[1]` is a valid PID.
**Suggestion:** Use `ps` with explicit `-o` format specifier for reliable column extraction.

### 6. Test coverage gaps
- `SettingsFactory` has no tests (env var parsing, defaults, missing vars, invalid integers)
- `MonitorStocksScript.run()` has zero tests for the main orchestration loop
- `infrastructure/logging.py` is completely untested (verbose/debug branching, file handler)
- `InMemoryStockRepository` / `InMemoryMarketTransitionRepository` lack direct unit tests

### 17. Tests call private methods on `Stock`
**File:** `tests/domain/test_stocks.py`
**Violation:** Test quality
Many tests call `stock._has_crossed_sma()`, `stock._is_close_to_sma()`, etc. — coupled to
implementation details rather than testing through the public API.
**Suggestion:** Test these behaviors through `generate_notifications()` instead.

### 18. `test_stocks.py` uses flat functions instead of test classes
**File:** `tests/domain/test_stocks.py`
**Violation:** Consistency
80+ test functions at module level. All other test files use `class Test*` grouping.
**Suggestion:** Group into classes by feature (e.g., `TestSMACrossing`, `TestGenerateNotifications`).

### 19. Duplicated percentage-change formula
**Files:** `domain/notifications.py`, `domain/stocks.py`
**Violation:** DRY
`((a - b) / b) * 100` appears in 3 places across two files.
**Suggestion:** Extract a `calculate_percentage_change(current, reference)` domain utility.

### 20. SMA-distance percentage computed twice
**File:** `domain/stocks.py`
**Violation:** DRY
`_is_close_to_sma` computes the percentage, then `_generate_close_to_*_notification` recomputes
the same value from scratch.
**Suggestion:** Have `_is_close_to_sma` return the percentage (or `None`) so callers reuse it.

### 21. 8 near-identical percentage notification factory methods
**File:** `domain/notifications.py`
**Violation:** OCP, DRY
Each `create_*_percent_increase/decrease` method is a trivial delegation to `_create_price_change`
differing only in `NotificationType` and verb.
**Suggestion:** Replace with a single `create_price_change(notification_type, symbol,
current_price, change_percentage)` that derives the verb from the sign of `change_percentage`.

### 22. Unnecessary `del` in `YahooFinanceProvider.get_stock`
**File:** `infrastructure/providers.py`
**Violation:** Clean Code
`del info, ticker_obj` is unnecessary — locals are GC'd on return.
**Suggestion:** Remove the line.

### 23. `StockProvider.get_stock` appears unused
**File:** `application/interfaces.py`
**Violation:** ISP
No use case or service calls `get_stock`. Implementors are forced to implement a method the
application layer doesn't need.
**Suggestion:** Verify usage; if unused, remove from the port interface.

### 24. `StockDTO.market_state` converts enum to raw string
**File:** `application/dtos.py`
**Violation:** Clean Code
`MarketState` enum is converted to `str` at the DTO boundary. The DTO is in the application
layer, which can reference domain types. Presentation loses type safety.
**Suggestion:** Use `MarketState | None` in the DTO; convert to string at the presentation layer.

### 25. `StopMonitorCommand` uses `TextIOBase` while `InteractiveMenu` uses `TextIO`
**Files:** `presentation/console/commands/stop_monitor.py`, `menu.py`
**Violation:** Consistency
Different type annotations for the same stream concept.
**Suggestion:** Standardize on `TextIO` from `typing` across both files.

### 26. `utils.py` line exceeds 100-character limit
**File:** `presentation/console/utils.py`
**Violation:** PEP 8
The `summary` f-string on the `format_send_messages_result` function is 103 characters.
**Suggestion:** Break the f-string across multiple lines.

---

## DDD Context Note

`Stock` is the **aggregate root**. It is correct and expected for it to:
- Hold state (prices, averages, market state)
- Enforce domain invariants
- Emit domain events via `generate_notifications()`

The SRP/OCP flags raised by automated analysis do not apply here — this is standard DDD
aggregate behavior.

---

## Priority Summary

| Priority | # | Item |
|---|---|---|
| Medium | 1 | `CheckReadinessCommand` → Checker strategy pattern |
| Medium | 2 | `tuple` instead of `list` in `SymbolConfig` |
| Medium | 3 | Add `from e` in `ConfigManager` exception re-raise (all 3 branches) |
| Medium | 4 | Fix `logging.py` env access + magic constants |
| Medium | 7 | `NotificationService` ignores send failures |
| Medium | 8 | Dead exception classes — wire or remove |
| Medium | 9 | `FireAndForgetMessageSender` LSP violation |
| Medium | 10 | `TelegramMessageSender` inconsistent error handling + leaking exceptions |
| Medium | 11 | `YahooFinanceProvider` inconsistent exception handling |
| Medium | 12 | `SettingsFactory` misleading exception + missing validation |
| Medium | 13 | Duplicated process listing format |
| Medium | 14 | `StopMonitorCommand` bypasses Command I/O contract |
| Medium | 15 | `ConfigManager` loses Decimal precision via `float()` |
| Medium | 16 | `ConfigRefresher.refresh()` silently swallows exceptions |
| Low | 5 | Fragile `ps aux` parsing |
| Low | 6 | Test coverage gaps (SettingsFactory, MonitorStocksScript, logging, repositories) |
| Low | 17 | Tests call private methods on `Stock` |
| Low | 18 | `test_stocks.py` flat functions instead of test classes |
| Low | 19 | Duplicated percentage-change formula |
| Low | 20 | SMA-distance percentage computed twice |
| Low | 21 | 8 near-identical percentage factory methods |
| Low | 22 | Unnecessary `del` in `YahooFinanceProvider` |
| Low | 23 | `StockProvider.get_stock` appears unused (ISP) |
| Low | 24 | `StockDTO.market_state` converts enum to string unnecessarily |
| Low | 25 | `TextIOBase` vs `TextIO` inconsistency |
| Low | 26 | `utils.py` line exceeds 100-char limit |
