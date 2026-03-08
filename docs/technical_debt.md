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

### 4. `logging.py` accesses `os.environ` directly
**File:** `infrastructure/logging.py`
Inconsistent with the `SettingsFactory` pattern used elsewhere. Also has unexplained
magic constants (`5 * 1024 * 1024`, `backupCount=3`).
**Suggestion:** Either use `SettingsFactory` or extract constants with explanatory names.

---

## Minor

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
| Medium | 4 | Fix `logging.py` env access + magic constants |
| Low | 26 | `utils.py` line exceeds 100-char limit |
