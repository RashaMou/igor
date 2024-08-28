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

    def _initialize_discord_client(self):
        client = DiscordAPI(self.bot_token)
        return client

    def start_listening(self):
        # start the gateway i guess?
        pass

    async def connect(self):
        await self.discord.connect()

    def igor_event_from_discord_event(self, discord_event):
        pass
        # initialize event here

    async def send_message(self, message):
        await self.discord.send_message(message, "general")
