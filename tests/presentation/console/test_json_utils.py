"""Unit tests for JSON utilities."""

import json
from decimal import Decimal

import pytest

from pryces.presentation.console.json_utils import DecimalEncoder, to_json


class TestDecimalEncoder:
    """Test suite for DecimalEncoder."""

    def test_encodes_decimal_as_string(self):
        data = {"price": Decimal("123.45")}
        result = json.dumps(data, cls=DecimalEncoder)
        assert result == '{"price": "123.45"}'

    def test_preserves_decimal_precision(self):
        data = {"value": Decimal("0.123456789")}
        result = json.dumps(data, cls=DecimalEncoder)
        assert result == '{"value": "0.123456789"}'

    def test_handles_non_decimal_types(self):
        data = {"string": "test", "number": 42, "boolean": True, "null": None}
        result = json.dumps(data, cls=DecimalEncoder)
        parsed = json.loads(result)
        assert parsed == data

    def test_handles_nested_decimals(self):
        data = {
            "outer": {
                "inner": Decimal("99.99"),
                "list": [Decimal("1.1"), Decimal("2.2")]
            }
        }
        result = json.dumps(data, cls=DecimalEncoder)
        parsed = json.loads(result)
        assert parsed["outer"]["inner"] == "99.99"
        assert parsed["outer"]["list"] == ["1.1", "2.2"]


class TestToJson:
    """Test suite for to_json function."""

    def test_returns_formatted_json_string(self):
        data = {"key": "value"}
        result = to_json(data)
        assert isinstance(result, str)
        assert json.loads(result) == data

    def test_uses_default_indent_of_2(self):
        data = {"key": "value"}
        result = to_json(data)
        assert result == '{\n  "key": "value"\n}'

    def test_allows_custom_indent(self):
        data = {"key": "value"}
        result = to_json(data, indent=4)
        assert result == '{\n    "key": "value"\n}'

    def test_handles_decimal_values_automatically(self):
        data = {"price": Decimal("123.45")}
        result = to_json(data)
        parsed = json.loads(result)
        assert parsed["price"] == "123.45"

    def test_handles_complex_data_with_decimals(self):
        data = {
            "success": True,
            "data": {
                "symbol": "AAPL",
                "price": Decimal("150.25"),
                "change": Decimal("-2.50")
            }
        }
        result = to_json(data)
        parsed = json.loads(result)
        assert parsed["data"]["price"] == "150.25"
        assert parsed["data"]["change"] == "-2.50"

    def test_accepts_additional_json_dumps_kwargs(self):
        data = {"b": 2, "a": 1}
        result = to_json(data, sort_keys=True)
        assert result == '{\n  "a": 1,\n  "b": 2\n}'
