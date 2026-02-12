from pathlib import Path
import platform
import os


def get_data_dir() -> Path:
    system = platform.system()

    if system == "Windows":
        base = Path(os.getenv("APPDATA", Path.home()))
        return base / "Nexus"

    return Path.home() / ".nexus"


def get_identity_path() -> Path:
    return get_data_dir() / "identity.json"
