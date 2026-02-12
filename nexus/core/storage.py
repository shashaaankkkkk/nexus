import sqlite3
import time
from pathlib import Path

from nexus.core.config import get_data_dir


class Storage:
    def __init__(self):
        self.db_path = get_data_dir() / "nexus.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        )
        """)

        self.conn.commit()

    def save_message(self, message_id: str, sender: str, content: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO messages (id, sender, content, timestamp) VALUES (?, ?, ?, ?)",
            (message_id, sender, content, int(time.time()))
        )
        self.conn.commit()

    def load_messages(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp ASC")
        return cursor.fetchall()
