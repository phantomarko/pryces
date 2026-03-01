# Volume-Based Notifications — Research

## Status: Research complete, implementation pending

---

## yfinance Volume Fields

| Field | What it represents |
|---|---|
| `info['regularMarketVolume']` | Intraday cumulative volume — grows from 0 at open to full-day total by close |
| `info['averageVolume']` | ~65-day (3-month) daily average. Listed as "retired" in yfinance source but still commonly populated |
| `info['averageVolume10days']` | 10-day daily average. Alias: `averageDailyVolume10Day` |
| `fast_info.ten_day_average_volume` | Same 10-day average, computed from OHLCV history — more reliable than `.info` |
| `fast_info.three_month_average_volume` | Same 3-month average, computed from OHLCV history — more reliable than `.info` |

**Reliability note**: `.info` volume averages are "retired keys" in yfinance's `quote.py`. The `fast_info` properties are computed directly from historical OHLCV data and are preferred. However, `fast_info` requires a second attribute access on the `Ticker` object, which may add latency.

---

## The Core Challenge: Intraday vs. Daily Comparison

`regularMarketVolume` is a partial-day cumulative total. `averageVolume` is a full-day total. They are not directly comparable. The standard approach is **projected daily volume**:

```
projected_daily_volume = regularMarketVolume / (minutes_since_open / 390)
RVOL = projected_daily_volume / average_daily_volume
```

Where 390 = total minutes in a US regular session (9:30–16:00 ET).

### Time-of-day distortion

The first 30–60 minutes of any session have structurally higher volume-per-minute (U-curve intraday distribution). This means RVOL computed near the open will be naturally inflated even on average days. A **time-of-day guard** — suppressing volume notifications in the first ~30 minutes — is required to avoid false positives at open.

An alternative to the full projection formula: only evaluate RVOL after the first hour, at which point the intraday cumulative is large enough to be meaningfully compared to the daily average.

---

## When to Notify — Thresholds and Signal Quality

### RVOL thresholds (industry standard)

| RVOL | Interpretation |
|---|---|
| < 1.0 | Below-average participation; price moves are less reliable |
| 1.0–1.5 | Normal; not actionable |
| 1.5–2.0 | Minimum for breakout confirmation (LuxAlgo / Schwab standard) |
| 2.0–3.0 | Strong — emerging institutional interest |
| 3.0–4.0 | Very strong — may also precede reversal rather than continuation |
| 4.0+ | Extreme — consider both continuation and exhaustion |

**Practical minimum for automated notification: RVOL ≥ 2.0.** Below 2x is too noisy.

### Combining volume with price movement

Volume alone generates too many false positives (high-volume sideways chop is not actionable). The standard combination:

- **RVOL ≥ 2.0 + price change ≥ ±1–2% from previous close** → breakout/breakdown confirmation (high confidence)
- **RVOL ≥ 2.0 + no price move** → accumulation/distribution signal (lower confidence, optional)

### Averaging period

- **10-day average**: best for intraday/momentum use cases — recent, smoothed over 2 trading weeks
- **3-month average**: better for liquidity assessment or institutional context
- For Pryces: **10-day** is the most appropriate baseline

---

## Design Options

### Option A — Simple: one notification per session

- One `HIGH_VOLUME` notification type, suppressed by existing `NotificationType` deduplication
- Triggers when: projected RVOL ≥ 2.0 AND |price change from previous close| ≥ 1%
- Skip first 30 min of session
- **Pro**: simple, low noise, minimal new code
- **Con**: won't escalate if volume reaches 3x or 4x

### Option B — Ladder: per-threshold notifications (recommended)

- Three notification types: `VOLUME_2X`, `VOLUME_3X`, `VOLUME_4X`
- Each fires once per session when projected RVOL crosses that integer multiple
- Optionally gated on a minimum price move
- **Pro**: mirrors existing `FIVE_PERCENT_INCREASE / TEN_PERCENT_INCREASE` ladder pattern; graded signal
- **Con**: more types, slightly more logic

### Option C — No price gate (pure RVOL signal)

- Fires on RVOL threshold alone, regardless of price direction
- Useful for detecting early accumulation before a price move
- **Con**: higher false-positive rate

---

## Implementation Notes

### Fields to add to `Stock` entity

```python
volume: int | None                    # regularMarketVolume — intraday cumulative
average_volume: int | None            # 10-day daily average
```

### Fields to add to `YahooFinanceMapper`

```python
volume = info.get("regularMarketVolume") or info.get("volume")
average_volume = info.get("averageVolume10days") or info.get("averageDailyVolume10Day")
# Fallback: use fast_info if .info fields are missing/unreliable
```

### RVOL computation (domain or application layer)

The projection formula requires knowing `minutes_since_open`, which means time-awareness. Options:
1. Compute RVOL in the domain (`Stock.generate_notifications`) by injecting or passing current time
2. Compute projected RVOL as a field in `Stock` itself (set by the provider or a service)
3. Compute in the application layer and pass as a derived field on the DTO

Option 1 keeps domain logic self-contained but requires passing a clock — consistent with `DelayWindowChecker`'s injectable clock pattern.

### Deduplication

The existing `_has_notification_type()` check in `Stock` handles per-session deduplication automatically. For the ladder approach (Option B), each threshold level is its own `NotificationType`, so they deduplicate independently — identical to how percentage change thresholds work.

---

## Open Questions

- Should the price gate be applied (combine RVOL + price move), or fire on RVOL alone?
- Accept `fast_info` latency cost, or rely on `.info` averages despite "retired" status?
- Time-of-day guard: hard-coded 30-min delay, or configurable?
- Single `HIGH_VOLUME` type (Option A) or ladder `VOLUME_2X/3X/4X` (Option B)?

---

## Sources

- [yfinance GitHub — quote.py (retired keys)](https://github.com/ranaroussi/yfinance/blob/main/yfinance/scrapers/quote.py)
- [Relative Volume RVOL — StockCharts ChartSchool](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/relative-volume-rvol)
- [Volume Confirms Breakouts — LuxAlgo](https://www.luxalgo.com/blog/how-volume-confirms-breakouts-in-trading/)
- [RVOL: From Noise to Signal — Adam Grimes](https://www.adamhgrimes.com/from-noise-to-signal-building-the-rvol-relative-volume-measure/)
- [Strong Volume Alert — Trade-Ideas](https://www.trade-ideas.com/help/alert/SV/)
- [Average Daily Trading Volume — Corporate Finance Institute](https://corporatefinanceinstitute.com/resources/career-map/sell-side/capital-markets/average-daily-trading-volume-adtv/)
- [Volume Spike Trading Signals — TradeFundrr](https://tradefundrr.com/volume-spike-trading-signals/)
