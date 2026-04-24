from datetime import datetime
from unittest.mock import Mock

import pytest

from pryces.application.interfaces import MessageSender
from pryces.infrastructure.formatters import ConsolidatingNotificationFormatter

_NOW = datetime(2024, 1, 1, 12, 0, 0)


@pytest.fixture
def mock_sender():
    return Mock(spec=MessageSender)


@pytest.fixture
def formatter():
    return ConsolidatingNotificationFormatter()


@pytest.fixture
def clock():
    return Mock(return_value=_NOW)


@pytest.fixture
def now():
    return _NOW
