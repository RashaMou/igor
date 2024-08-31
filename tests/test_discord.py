import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from igor.channels.discord import Discord
from igor.event import Event

@pytest.fixture
def discord_channel(hub):
    channel = Discord(hub)
    return channel

@pytest.mark.asyncio
async def test_discord_methods(discord_channel):
    connect_event = asyncio.Event()
    event_processed = asyncio.Event()

    async def mock_keep_connected(self):
        connect_event.set()
        while discord_channel.running:
            await asyncio.sleep(0.1)

    async def mock_listen_for_events(self):
        # Wait for connection before processing events
        await connect_event.wait()
        event = Event(
            channel="discord",
            type="message",
            content="igor echo test message",
            discord_channel_id="1234"
        )
        await discord_channel.hub.process_event(event)
        event_processed.set()

    async def mock_process_event(event):
        print(f"mock_process_event called with event: {event}")

    with patch.object(Discord, 'keep_connected', new=mock_keep_connected), \
         patch.object(Discord, 'listen_for_events', new=mock_listen_for_events):
 
        discord_channel.hub.process_event = AsyncMock(side_effect=mock_process_event)

        # create_task is non_blocking, so it simulates start_listening()
        # running in the background
        listen_task = asyncio.create_task(discord_channel.start_listening())

        try:
            # Wait for the event to be processed
            await asyncio.wait_for(event_processed.wait(), timeout=5.0)

            assert discord_channel.running == True
 
            discord_channel.hub.process_event.assert_called_once()

            called_event = discord_channel.hub.process_event.call_args[0][0]
            assert isinstance(called_event, Event)
            assert called_event.type == "message"
            assert called_event.content == "igor echo test message"
            assert called_event.channel == "discord"
            assert called_event.discord_channel_id == "1234"

        finally:
            await discord_channel.stop_listening()
            await listen_task  # Ensure the listen task is properly cleaned up
