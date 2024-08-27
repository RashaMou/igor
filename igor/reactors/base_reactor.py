import asyncio
from abc import ABC, abstractmethod
from igor.event import Event


class Reactor(ABC):
    def __init__(self, hub):
        self.hub = hub

    @abstractmethod
    async def can_handle(self, event: Event):
        pass

    @abstractmethod
    def handle(self, event: Event):
        pass

