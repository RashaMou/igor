import os
import pytest
import logging
from igor.hub import Hub
from igor.event import Event
from unittest.mock import MagicMock, AsyncMock
from tests.channels.mockchannel import MockChannel


@pytest.fixture
def config_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "config.toml")


@pytest.fixture
def hub(config_path):
    hub = Hub(config_path)

    hub.send_channel_response = AsyncMock()
    hub.signal_shutdown = MagicMock()

    yield hub
    # hub teardown


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


@pytest.fixture
async def mock_channel(hub, request):
    name = request.param
    channel = MockChannel(hub, name)
    yield channel
    # teardown
    await channel.stop_listening()
    channel.clear_sent_responses()


@pytest.fixture
def new_event():
    def _create_event(event_type, channel, content, **kwargs):
        return Event(event_type=event_type, channel=channel, content=content, **kwargs)

    return _create_event
