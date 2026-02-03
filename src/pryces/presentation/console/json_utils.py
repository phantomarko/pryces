"""JSON utilities for console output formatting."""

import json
from decimal import Decimal
from typing import Any


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Decimal types.

    Converts Decimal to string to preserve precision in JSON output.
    """

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def to_json(data: dict, **kwargs) -> str:
    """Serialize data to JSON string with DecimalEncoder and formatting.

    Uses DecimalEncoder by default and indents by 2 spaces for readability.
    """
    if 'indent' not in kwargs:
        kwargs['indent'] = 2

    kwargs['cls'] = DecimalEncoder

    return json.dumps(data, **kwargs)
