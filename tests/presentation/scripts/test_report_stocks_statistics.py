from unittest.mock import Mock, patch

import pytest

from pryces.application.use_cases.trigger_stocks_statistics import TriggerStocksStatistics
from pryces.presentation.scripts.report_stocks_statistics import ReportStocksStatisticsScript


@pytest.fixture()
def trigger_stocks_statistics():
    return Mock(spec=TriggerStocksStatistics)


@pytest.fixture()
def logger_factory():
    factory = Mock()
    factory.get_logger.return_value = Mock()
    return factory


def _make_script(trigger_stocks_statistics, logger_factory):
    return ReportStocksStatisticsScript(
        trigger_stocks_statistics=trigger_stocks_statistics,
        logger_factory=logger_factory,
    )


class TestReportStocksStatisticsScript:
    def test_does_not_trigger_when_no_symbols_tracked(
        self, trigger_stocks_statistics, logger_factory
    ):
        script = _make_script(trigger_stocks_statistics, logger_factory)

        with patch(
            "pryces.presentation.scripts.report_stocks_statistics.get_all_tracked_symbols",
            return_value=[],
        ):
            script.run()

        trigger_stocks_statistics.handle.assert_not_called()

    def test_triggers_statistics_for_all_tracked_symbols(
        self, trigger_stocks_statistics, logger_factory
    ):
        script = _make_script(trigger_stocks_statistics, logger_factory)

        with patch(
            "pryces.presentation.scripts.report_stocks_statistics.get_all_tracked_symbols",
            return_value=["AAPL", "GOOGL"],
        ):
            script.run()

        request = trigger_stocks_statistics.handle.call_args[0][0]
        assert request.symbols == ["AAPL", "GOOGL"]

    def test_triggers_once_for_all_symbols(self, trigger_stocks_statistics, logger_factory):
        script = _make_script(trigger_stocks_statistics, logger_factory)

        with patch(
            "pryces.presentation.scripts.report_stocks_statistics.get_all_tracked_symbols",
            return_value=["AAPL", "GOOGL"],
        ):
            script.run()

        trigger_stocks_statistics.handle.assert_called_once()
