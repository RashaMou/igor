from igor.response import Response
from igor.reactors.base_reactor import Reactor

class EchoReactor(Reactor):
    def __init__(self, hub):
        super().__init__(hub)

    def can_handle(self, event):
        return event.type == "message" and event.content.lower().startswith("igor echo")

    async def handle(self, event):
        message = event.content.lower().split("igor echo")
        message = ''.join(message).strip()
        if message == '':
            message = "You didn't say anything"
        return Response(
            content=message
        )
