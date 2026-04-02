from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class NotificationResult:
    messages: list[str]
    fulfilled_targets: list[Decimal]
