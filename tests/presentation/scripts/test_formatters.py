from decimal import Decimal

from pryces.application.dtos import PriceChangeDTO, StockStatisticsDTO
from pryces.presentation.scripts.formatters import format_stats


def _make_price_change(period: str, close_price: str, change_pct: str) -> PriceChangeDTO:
    close = Decimal(close_price)
    pct = Decimal(change_pct)
    change = close * pct / 100
    return PriceChangeDTO(period=period, close_price=close, change=change, change_percentage=pct)


def _make_dto(**overrides) -> StockStatisticsDTO:
    defaults = {
        "symbol": "AAPL",
        "current_price": Decimal("182.50"),
        "price_changes": [
            _make_price_change("1D", "181.20", "0.72"),
            _make_price_change("1W", "179.00", "-1.96"),
        ],
    }
    defaults.update(overrides)
    return StockStatisticsDTO(**defaults)


class TestFormatStats:
    def test_header_contains_symbol_and_current_price(self):
        result = format_stats(_make_dto())

        assert result.startswith("📊 AAPL — 182.50")

    def test_positive_change_shows_plus_sign_and_up_icon(self):
        result = format_stats(_make_dto())

        assert "+0.72%" in result
        assert "📈" in result

    def test_negative_change_shows_no_plus_sign_and_down_icon(self):
        result = format_stats(_make_dto())

        assert "-1.96%" in result
        assert "📉" in result

    def test_each_period_appears_on_its_own_line(self):
        result = format_stats(_make_dto())
        lines = result.splitlines()

        periods = [line for line in lines if "1D" in line or "1W" in line]
        assert len(periods) == 2

    def test_empty_price_changes_shows_fallback_message(self):
        dto = _make_dto(price_changes=[])

        result = format_stats(dto)

        assert "No historical data available" in result

    def test_empty_price_changes_still_includes_header(self):
        dto = _make_dto(price_changes=[])

        result = format_stats(dto)

        assert result.startswith("📊 AAPL — 182.50")

    def test_close_price_appears_in_output(self):
        result = format_stats(_make_dto())

        assert "181.20" in result
        assert "179.00" in result
