from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Event:
    event_type: str
    content: str
    channel: str
    extra: Dict[str, Any] = field(default_factory=dict)
