from igor.response import Response
from igor.reactors.base_reactor import Reactor
import aiohttp
from igor.logging_config import get_logger

logger = get_logger(__name__)


class CatPic(Reactor):
    def __init__(self, hub):
        super().__init__(hub)
        self.url = "https://api.thecatapi.com/v1/images/search"

    def can_handle(self, event):
        return event.event_type == "message" and event.content.lower().startswith(
            "igor cat pic"
        )

    async def send_request(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()

    async def handle(self, event):
        res = await self.send_request()
        logger.info(f"Catpic res: {res[0]["url"]}")
        return Response(content=res[0]["url"], channel=event.channel)
