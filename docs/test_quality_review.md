# Test Quality Review

Analysis of the test suite against the project's quality directives:
- Test structure mirrors `src/` layout
- `@pytest.fixture` for shared setup, no repeated setup logic
- Test public API, not internal implementation
- Many small focused test functions over large multi-behavior tests
- Descriptive naming conventions
- Edge cases, error paths, and boundary conditions covered
- DRY principle, clean assertions, no unnecessary mocking

---

## MEDIUM Severity

### 10. `test_stocks.py` is 1977 lines

A single file covering stock creation, SMA crossing, notification generation, deduplication, and target prices. Hard to navigate and slow to scan for a specific concern.

**Potential split:**
- `test_stocks_creation.py`
- `test_stocks_notifications.py`
- `test_stocks_deduplication.py`
- `test_stocks_targets.py`

**Affected file:** `tests/domain/test_stocks.py`

**Effort:** High — structural refactor

---

### 11. `TargetPriceDTO` has zero test coverage

The class exists in `dtos.py` alongside `StockDTO`, but `test_dtos.py` only tests `StockDTO`.

**Affected file:** `tests/application/test_dtos.py`

**Effort:** Low — add a few simple tests

---

### 12. Duplicate test — two tests cover identical scenario

Both `test_handle_counts_false_returns_as_failures` (lines 26-33) and `test_handle_counts_all_messages_as_failed` (lines 44-51) test the same "all fail" scenario. Neither tests the mixed success/failure case.

**Affected file:** `tests/application/use_cases/test_send_messages.py`

**Effort:** Low — delete one, add mixed success/failure test instead

---

### 13. Repeated `@patch` decorators

The same `get_config_files` patch is applied 6+ times across delete and edit command test files with near-identical patterns. Should be extracted into a fixture-based patching approach.

**Affected files:**
- `tests/presentation/console/commands/test_delete_config.py`
- `tests/presentation/console/commands/test_edit_config.py`

**Effort:** Medium — refactor into fixture-based patching

---

## LOW Severity

### 14. Missing edge case: division by zero in percentage calculations

`_calculate_percentage_change()` has no test for when the reference value is zero.

**Affected file:** `tests/domain/test_utils.py`

**Effort:** Low

---

### 15. Missing error path tests

No tests cover exceptions thrown by providers/senders, subprocess failures in monitor commands, or shutdown-with-pending-exceptions in fire-and-forget sender.

**Affected files:**
- `tests/application/test_services.py` — provider returns None, sender returns False
- `tests/infrastructure/test_fire_and_forget_message_sender.py` — shutdown with pending exceptions
- `tests/presentation/console/commands/test_monitor_stocks.py` — `subprocess.Popen` raises

**Effort:** Medium — requires understanding error contracts

---

### 16. Missing edge cases in factory settings tests

`test_factories.py` tests non-numeric values for `MAX_FETCH_WORKERS` but not empty strings or negative numbers.

**Affected file:** `tests/infrastructure/test_factories.py`

**Effort:** Low

---

### 17. Multi-behavior tests

A few tests assert multiple independent behaviors that could be separate focused functions.

**Affected:**
- `tests/presentation/console/commands/test_get_stocks_prices.py:21-35` — 4 separate string assertions in one test
- `tests/infrastructure/test_receivers.py:24-43` — tests parsing of multiple updates in one test

**Effort:** Low

---

### 18. Unused import

`pytest` is imported but never used.

**Affected file:** `tests/application/use_cases/test_get_stocks_prices.py:3`

**Effort:** Trivial

---

## What's Working Well

- **Naming** — consistently descriptive across all layers, follows `test_<scenario>_<expected_behavior>` pattern
- **No unnecessary mocking in domain** — tests use real objects and factory functions
- **Parametrized tests** — good use in providers (instrument types, currencies) and domain stock percentage thresholds
- **Directory structure** — properly mirrors `src/` layout throughout
- **Test granularity** — mostly small, focused test functions
- **Domain edge case coverage** — boundary testing for SMA crossings, target prices, and percentage thresholds is thorough
- **Repository tests** — clean identity checks (`is`) and comprehensive scenario coverage
- **Retry sender tests** — excellent coverage of exponential backoff, zero retries, and failure-then-recovery
