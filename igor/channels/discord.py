import asyncio

from igor.event import Event
from igor.external.discord import DiscordAPI


class Discord:
    """ """

    def __init__(self, hub, bot_token):
        self.hub = hub
        self.bot_token = bot_token
        self.discord = self._initialize_discord_client()

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
