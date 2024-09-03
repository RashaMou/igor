from dataclasses import dataclass, field



@dataclass
class Event:
    type: str
    content: str
    channel: str
    _extra: dict = field(default_factory=dict, init=False, repr=False)

    def __init__(self, type: str, content: str, channel: str, **kwargs):
        self.type = type
        self.content = content
        self.channel = channel
        self._extra = kwargs

    def __getattr__(self, name: str):
        if name in self._extra:
            return self._extra[name]
        raise AttributeError(f"'Event' object has no attribute '{name}'")
