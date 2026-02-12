import asyncio
import json


class Connection:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.peer_id = None

    async def perform_handshake(self, my_connect_id: str):
        # Send my identity
        self.writer.write(json.dumps({
            "type": "handshake",
            "connect_id": my_connect_id
        }).encode() + b"\n")
        await self.writer.drain()

        # Receive peer identity
        data = await self.reader.readline()
        message = json.loads(data.decode())

        if message.get("type") != "handshake":
            raise Exception("Invalid handshake")

        self.peer_id = message["connect_id"]

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()
