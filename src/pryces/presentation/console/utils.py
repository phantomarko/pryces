from __future__ import annotations

import subprocess
from pathlib import Path

from pryces.application.dtos import StockDTO

_MONITOR_MODULE = "pryces.presentation.scripts.monitor_stocks"


def get_running_monitors() -> list[tuple[str, str]]:
    result = subprocess.run(["ps", "-eo", "pid=,cmd="], capture_output=True, text=True)
    lines = result.stdout.splitlines()

    processes = []
    for line in lines:
        if _MONITOR_MODULE not in line:
            continue
        pid, cmd = line.strip().split(None, 1)
        try:
            cmd_parts = cmd.split()
            module_index = cmd_parts.index("-m") + 2
            config_path = cmd_parts[module_index] if module_index < len(cmd_parts) else "unknown"
        except ValueError:
            config_path = "unknown"
        processes.append((pid, config_path))

    return processes


def format_running_monitors(processes: list[tuple[str, str]]) -> str:
    header = f"Found {len(processes)} monitor process(es):"
    entries = [
        f"  {i + 1}. PID {pid} — config: {config_path}"
        for i, (pid, config_path) in enumerate(processes)
    ]
    return "\n".join([header] + entries)


def validate_symbol(value: str) -> bool:
    return bool(value and value.strip() and len(value.strip()) <= 10)


def validate_symbols(value: str) -> bool:
    if not value or not value.strip():
        return False

    symbols = [s.strip() for s in value.split(",")]
    return all(symbol and len(symbol) <= 10 for symbol in symbols)


def validate_positive_integer(value: str) -> bool:
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False


def validate_non_negative_integer(value: str) -> bool:
    if not value or not value.strip():
        return True  # empty string → caller defaults to 0
    try:
        return int(value.strip()) >= 0
    except (ValueError, TypeError):
        return False


def validate_file_path(value: str) -> bool:
    return bool(value and value.strip() and Path(value.strip()).is_file())


def parse_symbols_input(value: str) -> list[str]:
    symbols = [s.strip().upper() for s in value.split(",")]
    return [s for s in symbols if s]


FIELD_LABELS = [
    ("market_state", "Market State"),
    ("current_price", "Current Price"),
    ("previous_close_price", "Previous Close"),
    ("open_price", "Open"),
    ("day_high", "Day High"),
    ("day_low", "Day Low"),
    ("fifty_day_average", "50-Day Average"),
    ("two_hundred_day_average", "200-Day Average"),
    ("fifty_two_week_high", "52-Week High"),
    ("fifty_two_week_low", "52-Week Low"),
    ("price_delay_in_minutes", "Price delay (min)"),
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
