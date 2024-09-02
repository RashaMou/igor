from dataclasses import dataclass, field
from typing import Optional, Any

@dataclass
class Event:
    type: str
    content: str
    channel: str
    additional_fields: dict(field(default_factory=dict))

    def __init__(self, type: str, content: str, channel: str, **kwargs)
        self.type = type
        self.content = content
        self.channel = channel
        self.additional_fields = kwargs

    def __post_init__(self):
        # handle any additonal keyword arguments
        for key, value in self.additional_fields.items():
            setatrr(self, key, value)
        del self.additional_fields

