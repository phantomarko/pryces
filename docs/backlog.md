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

### 2. Retry policy for TelegramMessageSender

**Motivation:** The `TelegramMessageSender` currently fails immediately on any HTTP error, raising
`MessageSendingFailed`. Telegram API calls can fail transiently due to network hiccups, rate
limiting (HTTP 429), or temporary server errors (5xx). In the monitor script context, where
`FireAndForgetMessageSender` catches and logs these exceptions silently, a single transient failure
means a notification is permanently lost.

**Proposed retry parameters:**
- **Max retries:** 3 (total of 4 attempts — enough to survive transient issues without delaying
  indefinitely)
- **Backoff strategy:** Exponential — delays of 1s, 2s, 4s (base=1, factor=2)
- **Retryable conditions:** HTTP 429 (rate limited), HTTP 5xx (server errors), `URLError` (network
  connectivity issues)
- **Non-retryable conditions:** HTTP 4xx (except 429) — these indicate client errors (bad token,
  invalid chat ID) that won't resolve with retries

**Proposal:**
1. Create a `RetryMessageSender` decorator in the infrastructure layer implementing
   `MessageSender`. It wraps any `MessageSender` and retries failed calls with exponential backoff.
2. Accept retry parameters (max retries, base delay, backoff factor) via a frozen `RetrySettings`
   dataclass.
3. Only retry on transient failures — distinguish retryable vs non-retryable by inspecting
   `MessageSendingFailed` or exception type.
4. The decorator is composable: in the monitor script, the chain becomes
   `FireAndForgetMessageSender → RetryMessageSender → TelegramMessageSender`.
5. Wire retry settings at the composition roots (`cli.py` and `monitor_stocks.py`).

