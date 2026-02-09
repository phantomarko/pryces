from __future__ import annotations

from pryces.application.dtos import StockDTO

FIELD_LABELS = [
    ("marketState", "Market State"),
    ("currentPrice", "Current Price"),
    ("previousClosePrice", "Previous Close"),
    ("openPrice", "Open"),
    ("dayHigh", "Day High"),
    ("dayLow", "Day Low"),
    ("fiftyDayAverage", "50-Day Average"),
    ("twoHundredDayAverage", "200-Day Average"),
    ("fiftyTwoWeekHigh", "52-Week High"),
    ("fiftyTwoWeekLow", "52-Week Low"),
]

LABEL_WIDTH = max(len(label) for _, label in FIELD_LABELS)
SEPARATOR = "-" * 60
DOUBLE_SEPARATOR = "=" * 60


def format_stock(dto: StockDTO) -> str:
    parts: list[str] = []

    header = dto.symbol
    if dto.name:
        header += f" - {dto.name}"
    if dto.currency:
        header += f" ({dto.currency})"
    parts.append(header)

    for attr, label in FIELD_LABELS:
        value = getattr(dto, attr)
        if value is not None:
            parts.append(f"  {label + ':':<{LABEL_WIDTH + 1}}  {value}")

    return "\n".join(parts)


def format_stock_list(dtos: list[StockDTO], requested_count: int) -> str:
    parts: list[str] = []

    for i, dto in enumerate(dtos):
        parts.append(format_stock(dto))
        if i < len(dtos) - 1:
            parts.append("")
            parts.append(SEPARATOR)
            parts.append("")

    successful_count = len(dtos)
    failed_count = requested_count - successful_count

    if parts:
        parts.append("")
        parts.append(DOUBLE_SEPARATOR)

    summary = f"Summary: {requested_count} requested, {successful_count} successful, {failed_count} failed"
    parts.append(summary)

    return "\n".join(parts)
