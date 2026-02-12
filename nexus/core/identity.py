import json
import hashlib
from pathlib import Path
from nacl.signing import SigningKey
from nacl.encoding import Base64Encoder

from nexus.core.config import get_identity_path


class Identity:
    def __init__(self, private_key: SigningKey):
        self._private_key = private_key
        self._public_key = private_key.verify_key

    @property
    def public_key(self) -> str:
        return self._public_key.encode(Base64Encoder).decode()

    @property
    def connect_id(self) -> str:
        digest = hashlib.sha256(
            self._public_key.encode()
        ).hexdigest()
        return f"cx_{digest[:16]}"

    @classmethod
    def generate(cls) -> "Identity":
        return cls(SigningKey.generate())

    @classmethod
    def load_or_create(cls) -> "Identity":
        path = get_identity_path()

        if path.exists():
            data = json.loads(path.read_text())
            private_key = SigningKey(
                data["private_key"],
                encoder=Base64Encoder
            )
            return cls(private_key)

        identity = cls.generate()
        identity._save()
        return identity

    def _save(self) -> None:
        path = get_identity_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "private_key": self._private_key.encode(
                encoder=Base64Encoder
            ).decode()
        }

        path.write_text(json.dumps(data))
