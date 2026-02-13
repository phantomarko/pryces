# Pryces - Pending Memory Optimizations

Remaining improvements identified for free-tier deployment. Ordered by impact.

---

## 1. Cap ThreadPoolExecutor max workers

**Impact: HIGH** | **File:** `src/pryces/infrastructure/implementations.py:109`

### Problem

`max_workers=len(symbols)` creates one thread per symbol with no upper bound. Each thread reserves ~8 MB of stack space on Linux. Fetching 20 symbols = 20 threads = ~160 MB of stack space reserved.

```python
# Current
with ThreadPoolExecutor(max_workers=len(symbols)) as executor:
    results = list(executor.map(self._fetch_stock, symbols))
```

### Fix

```python
with ThreadPoolExecutor(max_workers=min(len(symbols), 5)) as executor:
    results = list(executor.map(self._fetch_stock, symbols))
```

### Benefit

Limits thread stack reservation from `N * 8MB` to `5 * 40MB`. The HTTP-bound nature of yfinance calls means 5 workers still provides good throughput since the bottleneck is network I/O, not CPU parallelism.

---

## 2. NotificationService: use `set` of types instead of `list` of full objects

**Impact: MEDIUM** | **File:** `src/pryces/application/services.py`

### Problem

`_notifications_sent` stores full `Notification` objects in a `list` per symbol, but `_already_sent()` only checks the notification **type** (via `equals()` which compares `_type` only). This means the service retains entire `Notification` objects (with their message strings) when it only needs to remember which `NotificationType` was already sent. Additionally, the `any()` linear scan is O(n) per check.

```python
# Current
self._notifications_sent: dict[str, list[Notification]] = {}

def _already_sent(self, symbol: str, notification: Notification) -> bool:
    if symbol not in self._notifications_sent:
        return False
    return any(notification.equals(sent) for sent in self._notifications_sent[symbol])
```

### Fix

Replace `dict[str, list[Notification]]` with `dict[str, set[NotificationType]]`:

```python
from pryces.domain.notifications import NotificationType

class NotificationService:
    def __init__(self, message_sender: MessageSender) -> None:
        self._message_sender = message_sender
        self._notifications_sent: dict[str, set[NotificationType]] = {}

    def send_stock_notifications(self, stock: Stock) -> list[Notification]:
        stock.generate_notifications()
        sent: list[Notification] = []

        for notification in stock.notifications:
            if self._already_sent(stock.symbol, notification):
                continue

            self._message_sender.send_message(notification.message)
            self._notifications_sent.setdefault(stock.symbol, set()).add(notification.type)
            sent.append(notification)

        return sent

    def _already_sent(self, symbol: str, notification: Notification) -> bool:
        return notification.type in self._notifications_sent.get(symbol, set())
```

### Benefit

Stores enum values (~28 bytes each) instead of full Notification objects (~300+ bytes each with message strings). Changes duplicate lookup from O(n) to O(1). Max 12 types per symbol = bounded to ~336 bytes per symbol no matter how long the process runs.

---

## 3. Use RotatingFileHandler instead of FileHandler for logging

**Impact: MEDIUM** | **File:** `src/pryces/infrastructure/logging.py:23`

### Problem

Uses a plain `FileHandler`. In a long-running monitor script, the log file grows indefinitely. On a free-tier machine with limited disk, this can fill the filesystem and ultimately crash the process.

```python
# Current
file_handler = logging.FileHandler(Path(logs_directory) / filename)
```

### Fix

```python
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler(
    Path(logs_directory) / filename,
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
)
```

### Benefit

Caps log disk usage to ~20 MB max (5 MB x 4 files) instead of unbounded growth. Prevents disk exhaustion on constrained machines.

---

## 4. Release yfinance objects early

**Impact: MEDIUM** | **File:** `src/pryces/infrastructure/implementations.py:93-96`

### Problem

`yf.Ticker(symbol).info` returns a dictionary with 100+ keys (~5-15 KB per symbol). The code only uses ~12 keys. The `Ticker` object and its `info` dict linger in memory until the GC collects them.

```python
# Current
def get_stock(self, symbol: str) -> Stock | None:
    self._logger.info(f"Fetching data for symbol: {symbol}")
    ticker_obj = yf.Ticker(symbol)
    return self._build_stock_from_ticker(symbol, ticker_obj.info)
```

### Fix

```python
def get_stock(self, symbol: str) -> Stock | None:
    self._logger.info(f"Fetching data for symbol: {symbol}")
    ticker_obj = yf.Ticker(symbol)
    info = ticker_obj.info
    stock = self._build_stock_from_ticker(symbol, info)
    del info, ticker_obj
    return stock
```

### Benefit

Ensures yfinance objects don't linger between GC cycles. With 20 symbols in a ThreadPoolExecutor, this can free 100-300 KB sooner per fetch cycle.
