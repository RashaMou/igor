import asyncio
import os

from igor.channels.base_channel import Channel
from igor.event import Event
from igor.external.discord_api import DiscordAPI
from dotenv import load_dotenv

load_dotenv()

class Discord(Channel):
    def __init__(self, hub):
        super().__init__(hub)
        self.bot_token = os.getenv('DISCORD_BOT_TOKEN')
        self.api = DiscordAPI(self.bot_token)
        self.running = False

    async def start_listening(self):
        self.running = True
        self.connection_task = asyncio.create_task(self.keep_connected())
        self.listen_task = asyncio.create_task(self.listen_for_events())

    async def stop_listening(self):
        self.running = False
        if hasattr(self, 'connection_task'):
            self.connection_task.cancel()
        if hasattr(self, 'listen_task'):
            self.listen_task.cancel()
 
    async def keep_connected(self):
        while self.running:
            try:
                await self.api.connect()
            except Exception as e:
                print(f"Connection error: {e}, reconnecting...")
                await asyncio.sleep(5)
 
    async def listen_for_events(self):
        while self.running:
            try:
                discord_event = await self.api.get_next_event()
                if discord_event['d']['content'].lower().startswith("igor"):
                    igor_event = self.igor_event_from_discord_event(discord_event)
                    await self.hub.process_event(igor_event)
            except Exception as e:
                await asyncio.sleep(1)  # Avoid tight loop in case of recurring errors

    def igor_event_from_discord_event(self, discord_event):
        return Event(
            channel="discord",
            type="message",
            content=discord_event['d']['content'],
            discord_channel_id=discord_event['d']['channel_id']
        )

    async def send_response(self, event, response):
        await self.api.send_message(event.discord_channel_id, response)
