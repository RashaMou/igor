import pytest
from unittest.mock import AsyncMock, MagicMock
import asyncio
from igor.hub import Hub
from igor.event import Event
from igor.response import Response


@pytest.fixture
def config_path(tmp_path):
    config = tmp_path / "test_config.toml"
    config.write_text(
        """
[channels.test_channel]
class = "TestChannel"

[reactors.test_reactor]
class = "TestReactor"
        """
    )
    return str(config)


@pytest.fixture
def hub(config_path):
    hub = Hub(config_path)
    hub.send_channel_response = AsyncMock()
    return hub


@pytest.mark.asyncio
async def test_hub_initialization(hub):
    assert isinstance(hub, Hub)
    assert hub.config is not None
    assert "channels" in hub.config
    assert "reactors" in hub.config


@pytest.mark.asyncio
async def test_hub_initialize_channels(hub, monkeypatch):
    mock_channel = MagicMock()
    monkeypatch.setattr(
        hub,
        "get_class_by_name",
        lambda type, name: lambda *args, **kwargs: mock_channel,
    )

    hub.initialize_channels()

    assert "test_channel" in hub.channels
    assert hub.channels["test_channel"] == mock_channel


@pytest.mark.asyncio
async def test_hub_initialize_reactors(hub, monkeypatch):
    mock_reactor = AsyncMock()
    monkeypatch.setattr(
        hub,
        "get_class_by_name",
        lambda type, name: lambda *args, **kwargs: mock_reactor,
    )

    hub.initialize_reactors()

    assert len(hub.reactors) == 1
    assert hub.reactors[0] == mock_reactor


@pytest.mark.asyncio
async def test_hub_process_event(hub):
    event = Event(event_type="test", content="test content", channel="test_channel")
    mock_reactor = MagicMock()
    mock_reactor.can_handle = MagicMock(return_value=True)
    mock_reactor.handle = AsyncMock(
        return_value=Response(content="test response", channel="test_channel")
    )
    hub.reactors = [mock_reactor]

    await hub.process_event(event)

    mock_reactor.can_handle.assert_called_once_with(event)
    mock_reactor.handle.assert_awaited_once_with(event)
    hub.send_channel_response.assert_awaited_once_with(
        event, mock_reactor.handle.return_value
    )


@pytest.mark.asyncio
async def test_hub_process_event_no_handler(hub):
    event = Event(event_type="test", content="test content", channel="test channel")
    mock_reactor = MagicMock()
    mock_reactor.can_handle = MagicMock(return_value=False)
    hub.reactors = [mock_reactor]

    await hub.process_event(event)

    mock_reactor.can_handle.assert_called_once_with(event)
    mock_reactor.handle.assert_not_called()
    hub.send_channel_response.assert_not_called()


@pytest.mark.asyncio
async def test_hub_start(hub, monkeypatch):
    mock_channel = AsyncMock()
    monkeypatch.setattr(
        hub,
        "get_class_by_name",
        lambda type, name: lambda *args, **kwargs: mock_channel,
    )

    # We need to set the shutdown event after a short delay
    async def delayed_shutdown():
        await asyncio.sleep(0.1)
        hub.signal_shutdown()

    asyncio.create_task(delayed_shutdown())

    await hub.start()

    mock_channel.start_listening.assert_awaited_once()


@pytest.mark.asyncio
async def test_hub_signal_shutdown(hub):
    hub.tasks = [MagicMock(), MagicMock()]

    hub.signal_shutdown()

    assert hub.shutdown_event.is_set()
    for task in hub.tasks:
        task.cancel.assert_called_once()
