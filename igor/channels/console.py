import asyncio
from igor.event import Event
from igor.response import Response
from igor.channels.base_channel import Channel
from igor.logging_config import get_logger

logger = get_logger(__name__)


class Console(Channel):
    def __init__(self, hub):
        super().__init__(hub)

    async def start_listening(self):
        while True:
            try:
                user_input = await self.async_input("> ")
                if user_input.lower().startswith("igor"):
                    event = self.channel_event_to_igor_event(user_input)
                    await self.hub.process_event(event)
                elif user_input.lower() == "q":
                    await self.stop_listening()
                    print(f"{self.__class__.__name__} is shutting down")
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"An error occurred with the console listening: {e}")

    async def async_input(self, prompt):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, prompt)

    def channel_event_to_igor_event(self, event):
        return Event(type="message", content=event, channel="console")

    async def send_response(self, event: Event, response: Response):
        print(f"Igor: {response}")

    async def stop_listening(self):
        self.hub.signal_shutdown()
