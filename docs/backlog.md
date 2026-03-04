# Backlog

## Overview

This is the **feature and improvement backlog** for the Pryces codebase. It tracks new features,
logic improvements, and enhancements that are not technical debt (see `technical_debt.md` for that).

**How to use it:**
- Before starting a task, read the relevant item for full context.
- After completing an item, remove it from the backlog.
- Add new items as ideas emerge — include the motivation and a concrete description.

---

## Items

### 1. Logger abstraction — port interface + factory

**Motivation:** Currently, classes across infrastructure and presentation obtain loggers directly
via `logging.getLogger(__name__)`. This couples them to Python's `logging` module and violates DIP
— concrete logger usage is hardcoded rather than injected. The application layer has no logging at
all, partly because importing `logging` there would be an infrastructure concern leaking inward.

**Current state:**
- Infrastructure classes (`YahooFinanceProvider`, `YahooFinanceMapper`, `TelegramMessageSender`,
  `FireAndForgetMessageSender`) and presentation classes (`MonitorStocksScript`, `ConfigRefresher`,
  `CheckReadinessCommand`, `GetStocksPricesCommand`, `cli.main()`) all call
  `logging.getLogger(__name__)` directly in their `__init__` or at function scope.
- Domain and application layers do not log anything.

**Proposal:**
1. Define a `Logger` port interface in the application layer with the standard level methods
   (`debug`, `info`, `warning`, `error`).
2. Define a `LoggerFactory` port interface in the application layer with a single method
   `get_logger(name: str) -> Logger`.
3. Implement both in the infrastructure layer, wrapping Python's native `logging` module.
4. Inject `LoggerFactory` into classes that need logging. Each class calls
   `logger_factory.get_logger(__name__)` (or its module path) to obtain its `Logger` instance.
5. This allows the application layer to log through the abstraction without depending on
   infrastructure, and makes logging behavior testable and swappable.

