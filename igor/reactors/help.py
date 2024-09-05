from igor.response import Response
from igor.reactors.base_reactor import Reactor


class Help(Reactor):
    def __init__(self, hub):
        super().__init__(hub)

    def can_handle(self, event):
        return event.event_type == "message" and event.content.lower().startswith(
            "igor help"
        )

    async def handle(self, event):
        help_text = """
I'm a bot. Here are some things you can ask me:

- cat pic: I'll send you a random cat pic
- fortune: I'll send you a random fortune
- echo: Mostly for testing, I'll just repeat what you tell me
- sentiment: I use natural language processing to analyze the sentiment of some text
"""
        return Response(content=help_text, channel=event.channel)
