import asyncio


class TCPServer:
    def __init__(self, host: str, port: int, on_client_connected):
        self.host = host
        self.port = port
        self.on_client_connected = on_client_connected
        self.server = None

    async def start(self):
        self.server = await asyncio.start_server(
            self.on_client_connected,
            self.host,
            self.port
        )

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
