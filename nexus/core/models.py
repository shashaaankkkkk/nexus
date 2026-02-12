import uuid
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any


PROTOCOL_VERSION = 1


@dataclass
class Message:
    id: str
    version: int
    type: str
    sender: str
    content: str
    timestamp: int

    @classmethod
    def create(cls, sender: str, content: str) -> "Message":
        return cls(
            id=str(uuid.uuid4()),
            version=PROTOCOL_VERSION,
            type="text",
            sender=sender,
            content=content,
            timestamp=int(time.time())
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(**data)
