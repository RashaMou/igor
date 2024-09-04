from igor.channels.base_channel import Channel
from igor.event import Event
import logging


class MockChannel(Channel):
    def __init__(self, hub, name="MockChannel"):
        super().__init__(hub)
        self.name = name
        self.is_listening = False
        self.logger = logging.getLogger(__name__)
        self.sent_responses = []

    async def start_listening(self):
        self.is_listening = True
        self.logger.info(f"MockChannel {id(self)} started listening")

    async def stop_listening(self):
        self.is_listening = False
        self.logger.info(f"MockChannel {id(self)} stopped listening")

    async def send_response(self, event, response):
        self.sent_responses.append((event, response))
        self.logger.info(f"MockChannel {id(self)} sent response: {response}")

    def channel_event_to_igor_event(self, event) -> Event:
        return Event(type=event.type, content=event.content, channel=self.name)

    async def simulate_event(self, event):
        igor_event = self.channel_event_to_igor_event(event)
        await self.hub.process_event(igor_event)

    def clear_sent_responses(self):
        self.sent_responses = []
