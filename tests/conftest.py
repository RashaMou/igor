import os
import pytest
import logging
import asyncio
from igor.hub import Hub
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def config_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    igor_dir = os.path.dirname(current_dir)
    return os.path.join(igor_dir, 'igor', 'config.toml')

@pytest.fixture
def hub(config_path):
    hub = Hub(config_path)

    hub.send_response = AsyncMock()
    hub.signal_shutdown = MagicMock()

    return hub

@pytest.fixture
def hub_with_mocked_process(hub):
    hub.process_event = AsyncMock()
    return hub

@pytest.fixture
def unmocked_hub(config_path):
    return Hub(config_path)

@pytest.fixture(autouse=True)
def configure_logging():
    logging.basicConfig(level=logging.DEBUG)
