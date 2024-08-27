import asyncio
import random
from igor.response import Response
from igor.reactors.base_reactor import Reactor

class Fortune(Reactor):
    def __init__(self, hub):
        super().__init__(hub)
        self.fortunes = [
            "I didn’t come this far to only come this far",
            "Anything that you do, any accomplishment that you make, you have to work for"
        ]

    def can_handle(self, event):
        return event.type == "message" and event.content.lower().startswith("igor fortune")

    async def handle(self, event):
        fortune = random.choice(self.fortunes)
        return Response(
            content=fortune
        )

