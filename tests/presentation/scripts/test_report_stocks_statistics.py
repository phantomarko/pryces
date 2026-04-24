from unittest.mock import MagicMock, Mock, patch

import pytest

from pryces.application.use_cases.get_stocks_statistics import GetStocksStatistics
from pryces.application.use_cases.send_messages import SendMessages
from pryces.presentation.scripts.report_stocks_statistics import ReportStocksStatisticsScript


@pytest.fixture()
def get_stocks_statistics():
    return Mock(spec=GetStocksStatistics)


@pytest.fixture()
def send_messages():
    mock = Mock(spec=SendMessages)
    mock.handle.return_value = MagicMock(successful=1, failed=0)
    return mock


@pytest.fixture()
def logger_factory():
    factory = Mock()
    factory.get_logger.return_value = Mock()
    return factory


def _make_script(get_stocks_statistics, send_messages, logger_factory):
    return ReportStocksStatisticsScript(
        get_stocks_statistics=get_stocks_statistics,
        send_messages=send_messages,
        logger_factory=logger_factory,
    )


class TestReportStocksStatisticsScript:
    def test_does_not_send_when_no_symbols_tracked(
        self, get_stocks_statistics, send_messages, logger_factory
    ):
        script = _make_script(get_stocks_statistics, send_messages, logger_factory)

        with patch(
            "pryces.presentation.scripts.report_stocks_statistics.get_all_tracked_symbols",
            return_value=[],
        ):
            script.run()

        send_messages.handle.assert_not_called()
        get_stocks_statistics.handle.assert_not_called()

    def test_fetches_statistics_for_all_tracked_symbols(
        self, get_stocks_statistics, send_messages, logger_factory
    ):
        get_stocks_statistics.handle.return_value = ["msg1", "msg2"]
        script = _make_script(get_stocks_statistics, send_messages, logger_factory)

        with patch(
            "pryces.presentation.scripts.report_stocks_statistics.get_all_tracked_symbols",
            return_value=["AAPL", "GOOGL"],
        ):
            script.run()

        request = get_stocks_statistics.handle.call_args[0][0]
        assert request.symbols == ["AAPL", "GOOGL"]

    def test_sends_one_message_per_symbol(
        self, get_stocks_statistics, send_messages, logger_factory
    ):
        get_stocks_statistics.handle.return_value = ["msg_aapl", "msg_googl"]
        send_messages.handle.return_value = MagicMock(successful=2, failed=0)
        script = _make_script(get_stocks_statistics, send_messages, logger_factory)

        with patch(
            "pryces.presentation.scripts.report_stocks_statistics.get_all_tracked_symbols",
            return_value=["AAPL", "GOOGL"],
        ):
            script.run()

        request = send_messages.handle.call_args[0][0]
        assert len(request.messages) == 2

    def test_message_content_includes_symbol_and_price(
        self, get_stocks_statistics, send_messages, logger_factory
    ):
        get_stocks_statistics.handle.return_value = ["📊 AAPL — 182.50\n📈 1D   181.00  +0.83%"]
        script = _make_script(get_stocks_statistics, send_messages, logger_factory)

        with patch(
            "pryces.presentation.scripts.report_stocks_statistics.get_all_tracked_symbols",
            return_value=["AAPL"],
        ):
            script.run()

        request = send_messages.handle.call_args[0][0]
        assert "AAPL" in request.messages[0]
        assert "182.50" in request.messages[0]

    def test_sends_only_available_stats_when_provider_returns_subset(
        self, get_stocks_statistics, send_messages, logger_factory
    ):
        get_stocks_statistics.handle.return_value = ["msg_aapl"]
        send_messages.handle.return_value = MagicMock(successful=1, failed=0)
        script = _make_script(get_stocks_statistics, send_messages, logger_factory)

        with patch(
            "pryces.presentation.scripts.report_stocks_statistics.get_all_tracked_symbols",
            return_value=["AAPL", "GOOGL"],
        ):
            script.run()

        request = send_messages.handle.call_args[0][0]
        assert len(request.messages) == 1
