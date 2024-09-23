import pytest
from unittest.mock import AsyncMock, MagicMock
from igor.channels.base_channel import Channel
from igor.event import Event
from igor.response import Response


class DummyChannel(Channel):
    #  test abstract base classes by creating a minimal concrete implementation
    #  for testing purposes
    async def start_listening(self):
        pass

    async def stop_listening(self):
        pass

    def channel_event_to_igor_event(self, event):
        return Event(event_type="test", content=event, channel="test_channel")

    async def send_response(self, event, response):
        pass


@pytest.fixture
def hub():
    return MagicMock()


@pytest.fixture
def channel(hub):
    return DummyChannel(hub)


@pytest.mark.asyncio
async def test_channel_initialization(channel, hub):
    assert isinstance(channel, Channel)
    assert channel.hub == hub


@pytest.mark.asyncio
async def test_channel_event_conversion(channel):
    channel_event = "Test event"
    igor_event = channel.channel_event_to_igor_event(channel_event)
    assert isinstance(igor_event, Event)
    assert igor_event.event_type == "test"
    assert igor_event.content == channel_event
    assert igor_event.channel == "test_channel"


@pytest.mark.asyncio
async def test_channel_send_response(channel):
    # this ensures that code that uses a Channel object can call send_response
    # with the expected arguments
    event = Event(event_type="test", content="test content", channel="test_channel")
    response = Response(content="test response", channel="test_channel")

    # Mock the send_response method
    channel.send_response = AsyncMock()

    await channel.send_response(event, response)
    channel.send_response.assert_awaited_once_with(event, response)


@pytest.mark.asyncio
async def test_chanell_start_stop_listening(channel):
    channel.start_listening = AsyncMock()
    channel.stop_listening = AsyncMock()

    await channel.start_listening()
    channel.start_listening.assert_awaited_once()

    await channel.stop_listening()
    channel.stop_listening.assert_awaited_once()
