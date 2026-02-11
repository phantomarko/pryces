from decimal import Decimal

from pryces.presentation.console.output_utils import format_stock, format_stock_list
from tests.fixtures.factories import create_stock_dto


class TestFormatStock:

    def test_formats_stock_with_all_fields(self):
        dto = create_stock_dto(
            "AAPL",
            Decimal("150.25"),
            name="Apple Inc.",
            currency="USD",
            previousClosePrice=Decimal("148.50"),
            openPrice=Decimal("149.00"),
            dayHigh=Decimal("151.00"),
            dayLow=Decimal("148.00"),
            fiftyDayAverage=Decimal("145.50"),
            twoHundredDayAverage=Decimal("140.00"),
            fiftyTwoWeekHigh=Decimal("180.00"),
            fiftyTwoWeekLow=Decimal("120.00"),
        )

        result = format_stock(dto)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "Current Price:" in result
        assert "150.25" in result
        assert "Previous Close:" in result
        assert "148.50" in result
        assert "Open:" in result
        assert "149.00" in result
        assert "Day High:" in result
        assert "151.00" in result
        assert "Day Low:" in result
        assert "148.00" in result
        assert "50-Day Average:" in result
        assert "145.50" in result
        assert "200-Day Average:" in result
        assert "140.00" in result
        assert "52-Week High:" in result
        assert "180.00" in result
        assert "52-Week Low:" in result
        assert "120.00" in result

    def test_formats_stock_with_minimal_fields(self):
        dto = create_stock_dto(
            "AAPL",
            Decimal("150.25"),
            name=None,
            currency=None,
            previousClosePrice=None,
            openPrice=None,
            dayHigh=None,
            dayLow=None,
            fiftyDayAverage=None,
            twoHundredDayAverage=None,
            fiftyTwoWeekHigh=None,
            fiftyTwoWeekLow=None,
        )

        result = format_stock(dto)

        assert result.startswith("AAPL\n")
        assert "Current Price:" in result
        assert "150.25" in result
        assert "Previous Close:" not in result
        assert "Open:" not in result

    def test_omits_none_fields(self):
        dto = create_stock_dto(
            "AAPL",
            Decimal("150.25"),
            name="Apple Inc.",
            previousClosePrice=Decimal("148.50"),
            openPrice=None,
            dayHigh=None,
            dayLow=None,
            fiftyDayAverage=None,
            twoHundredDayAverage=None,
            fiftyTwoWeekHigh=None,
            fiftyTwoWeekLow=None,
        )

        result = format_stock(dto)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "Current Price:" in result
        assert "Previous Close:" in result
        assert "Open:" not in result
        assert "Day High:" not in result

    def test_header_without_name(self):
        dto = create_stock_dto("AAPL", Decimal("150.25"), name=None)

        result = format_stock(dto)

        lines = result.split("\n")
        assert lines[0] == "AAPL (USD)"

    def test_header_without_currency(self):
        dto = create_stock_dto("AAPL", Decimal("150.25"), name="Apple Inc.", currency=None)

        result = format_stock(dto)

        lines = result.split("\n")
        assert lines[0] == "AAPL - Apple Inc."

    def test_does_not_include_notifications(self):
        dto = create_stock_dto("AAPL", Decimal("150.25"))

        result = format_stock(dto)

        assert "notification" not in result.lower()

    def test_preserves_decimal_precision(self):
        dto = create_stock_dto(
            "GOOGL",
            Decimal("2847.123456789"),
            name=None,
            currency=None,
            previousClosePrice=None,
            openPrice=None,
            dayHigh=None,
            dayLow=None,
            fiftyDayAverage=None,
            twoHundredDayAverage=None,
            fiftyTwoWeekHigh=None,
            fiftyTwoWeekLow=None,
        )

        result = format_stock(dto)

        assert "2847.123456789" in result


class TestFormatStockList:

    def test_formats_multiple_stocks_with_separators(self):
        dtos = [
            create_stock_dto("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock_dto("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
        ]

        result = format_stock_list(dtos, requested_count=2)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "GOOGL - Alphabet Inc. (USD)" in result
        assert "------------------------------------------------------------" in result
        assert "============================================================" in result
        assert "Summary: 2 requested, 2 successful, 0 failed" in result

    def test_formats_single_stock_with_summary(self):
        dtos = [create_stock_dto("AAPL", Decimal("150.25"), name="Apple Inc.")]

        result = format_stock_list(dtos, requested_count=1)

        assert "AAPL - Apple Inc. (USD)" in result
        assert "------------------------------------------------------------" not in result
        assert "============================================================" in result
        assert "Summary: 1 requested, 1 successful, 0 failed" in result

    def test_formats_partial_failures(self):
        dtos = [
            create_stock_dto("AAPL", Decimal("150.25"), name="Apple Inc."),
            create_stock_dto("GOOGL", Decimal("2847.50"), name="Alphabet Inc."),
        ]

        result = format_stock_list(dtos, requested_count=3)

        assert "Summary: 3 requested, 2 successful, 1 failed" in result

    def test_formats_all_failures(self):
        result = format_stock_list([], requested_count=3)

        assert "============================================================" not in result
        assert "Summary: 3 requested, 0 successful, 3 failed" in result

    def test_three_stocks_have_two_separators(self):
        dtos = [
            create_stock_dto("AAPL", Decimal("150.25")),
            create_stock_dto("GOOGL", Decimal("2847.50")),
            create_stock_dto("MSFT", Decimal("350.75")),
        ]

        result = format_stock_list(dtos, requested_count=3)

        assert result.count("------------------------------------------------------------") == 2
        assert "Summary: 3 requested, 3 successful, 0 failed" in result
