import asyncio
from igor.event import Event
from igor.response import Response
from igor.channels.base_channel import Channel


class Console(Channel):
    def __init__(self, hub):
        super().__init__(hub)

    async def start_listening(self):
        while True:
            try:
                user_input = await self.async_input("> ")
                if user_input.lower().startswith("igor"):
                    event = Event(type="message", content=user_input, channel="console")
                    await self.hub.process_event(event)
                elif user_input.lower() == "q":
                    await self.stop_listening()
                    print(f"{self.__class__.__name__} is shutting down")
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"An error occurred: {e}")

    async def async_input(self, prompt):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, prompt)

    def channel_event_to_igor_event(self, event):
        return Event(event_type="message", content=event, channel="console")

    async def send_response(self, event: Event, response: Response):
        print(f"Igor: {response.content}")

    async def stop_listening(self):
        self.hub.signal_shutdown()
