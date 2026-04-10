from unittest.mock import Mock

import pytest

from pryces.infrastructure.providers import (
    YahooFinanceMapper,
    YahooFinanceStatisticsMapper,
)


@pytest.fixture
def mapper():
    return YahooFinanceMapper(extra_delay_in_minutes=0, logger_factory=Mock())


@pytest.fixture
def statistics_mapper():
    return YahooFinanceStatisticsMapper(logger_factory=Mock())
