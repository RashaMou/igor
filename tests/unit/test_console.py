import pytest
from unittest.mock import AsyncMock, MagicMock
from igor.channels.console import Console
from igor.event import Event
from igor.response import Response


@pytest.fixture
def hub():
    return MagicMock()


@pytest.fixture
def console_channel(hub):
    return Console(hub)


@pytest.mark.asyncio
async def test_console_channel_initialization(console_channel, hub):
    assert isinstance(console_channel, Console)
    assert console_channel.hub == hub


@pytest.mark.asyncio
async def test_console_channel_start_listening(console_channel, monkeypatch):
    # Mock the async_input method to return a sequence of inputs
    inputs = ["igor test", "regular message", "q"]

    async def mock_async_input(prompt):
        return inputs.pop(0)

    monkeypatch.setattr(console_channel, "async_input", mock_async_input)

    # Mock the hub's process_event method
    console_channel.hub.process_event = AsyncMock()

    # Run start_listening
    await console_channel.start_listening()

    # Check that process_event was called once with the correct event
    console_channel.hub.process_event.assert_called_once()
    called_event = console_channel.hub.process_event.call_args[0][0]
    assert isinstance(called_event, Event)
    assert called_event.event_type == "message"
    assert called_event.content == "igor test"
    assert called_event.channel == "console"


@pytest.mark.asyncio
async def test_console_channel_send_response(console_channel, capsys):
    event = Event(event_type="message", content="test content", channel="console")
    response = Response(content="test response", channel="console")

    await console_channel.send_response(event, response)

    captured = capsys.readouterr()
    assert captured.out.strip() == "Igor: test response"


@pytest.mark.asyncio
async def test_console_channel_stop_listening(console_channel):
    console_channel.hub.signal_shutdown = MagicMock()
    await console_channel.stop_listening()
    console_channel.hub.signal_shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_console_channel_event_conversion(console_channel):
    console_event = "test message"
    igor_event = console_channel.channel_event_to_igor_event(console_event)

    assert isinstance(igor_event, Event)
    assert igor_event.event_type == "message"
    assert igor_event.content == "test message"
    assert igor_event.channel == "console"
