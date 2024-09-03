import os

import asyncio
from igor.channels.base_channel import Channel
from igor.external.discord_api import DiscordAPI
from dotenv import load_dotenv
from igor.event import Event
from igor.logging_config import get_logger

load_dotenv()
logger = get_logger(__name__)


class Discord(Channel):
    def __init__(self, hub):
        super().__init__(hub)
        self.api = DiscordAPI(os.getenv("DISCORD_BOT_TOKEN"))
        self.running = False

    async def start_listening(self):
        self.running = True
        self.connection_task = asyncio.create_task(self.keep_connected())
        self.listen_task = asyncio.create_task(self.listen_for_events())

    async def stop_listening(self):
        self.running = False
        if hasattr(self, "connection_task"):
            self.connection_task.cancel()
        if hasattr(self, "listen_task"):
            self.listen_task.cancel()

    async def keep_connected(self):
        while self.running:
            try:
                await self.api.connect()
            except Exception as e:
                logger.debug(f"Connection error: {e}, reconnecting...")
                await asyncio.sleep(5)

    async def listen_for_events(self):
        while self.running:
            try:
                discord_event = await self.api.get_next_event()
                if discord_event["d"]["content"].lower().startswith("igor"):
                    igor_event = self.channel_event_to_igor_event(discord_event)
                    await self.hub.process_event(igor_event)
            except Exception as e:
                logger.debug(f"Error getting next discord event: {e}")
                await asyncio.sleep(1)  # Avoid tight loop in case of recurring errors

    def channel_event_to_igor_event(self, event):
        return Event(
            channel="discord",
            type="message",
            content=event["d"]["content"],
            discord_channel_id=event["d"]["channel_id"],
        )

    async def send_response(self, event, response):
        await self.api.send_message(event.discord_channel_id, response)
