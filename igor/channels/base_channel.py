import asyncio
from abc import ABC, abstractmethod
from igor.event import Event
from igor.response import Response


class Channel(ABC):
    def __init__(self, hub):
        self.hub = hub

    @abstractmethod
    async def start_listening(self):
        pass

    @abstractmethod
    def send_response(self, event: Event, response: Response):
        pass
