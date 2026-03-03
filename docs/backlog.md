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

---

### 2. Defer non-essential notifications when market opens

**Motivation:** When the market opens, `Stock.generate_notifications()` produces all applicable
notifications at once — market open, SMA proximity/crossings, percentage changes, 52-week
highs/lows, and target prices. This can result in a burst of messages that is hard to read,
especially for users monitoring multiple symbols.

**Current state:**
- `_generate_market_open_notifications()` calls all notification generators sequentially in a single
  invocation: market open, SMA checks, percentage changes, 52-week extremes, and target prices.
- All generated notifications are returned together and sent immediately.

**Proposal:**
When `generate_notifications()` produces a `REGULAR_MARKET_OPEN` notification for the first time,
it should return only that notification and skip the remaining generators. On the next call (after
the monitor script sleeps for the configured interval), all other applicable notifications will be
generated normally.

This spreads the notification load across two cycles:
- **First cycle after market opens:** Only the market open notification (with the opening price).
- **Second cycle:** SMA, percentage changes, 52-week extremes, target prices — the usual set.

The result is shorter, more readable notification batches. The delay is just one monitoring interval
(typically a few minutes), so no meaningful information is lost.

**Implementation hint:** After `_generate_regular_market_open_notification()`, check whether a new
`REGULAR_MARKET_OPEN` notification was just added in this call. If so, return early from
`_generate_market_open_notifications()` before running the remaining generators.
