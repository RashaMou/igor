from dataclasses import dataclass


@dataclass
class Event:
    type: str
    content: str
    channel: str

    def __init__(self, type: str, content: str, channel: str, **kwargs):
        self.type = type
        self.content = content
        self.channel = channel
        for key, value in kwargs.items():
            setattr(self, key, value)
