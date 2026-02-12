import asyncio
import json
import socket


DISCOVERY_PORT = 9999
BROADCAST_INTERVAL = 3


class DiscoveryService:
    def __init__(self, connect_id: str, tcp_port: int, on_peer_discovered):
        self.connect_id = connect_id
        self.tcp_port = tcp_port
        self.on_peer_discovered = on_peer_discovered
        self.transport = None

    async def start(self):
        loop = asyncio.get_running_loop()

        # Create UDP listener
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: self,
            local_addr=("0.0.0.0", DISCOVERY_PORT),
            allow_broadcast=True,
        )

        # Start broadcaster task
        asyncio.create_task(self._broadcast_loop())

    async def _broadcast_loop(self):
        while True:
            message = json.dumps({
                "type": "hello",
                "connect_id": self.connect_id,
                "tcp_port": self.tcp_port
            }).encode()

            self.transport.sendto(
                message,
                ("255.255.255.255", DISCOVERY_PORT)
            )

            await asyncio.sleep(BROADCAST_INTERVAL)

    # DatagramProtocol methods
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        try:
            message = json.loads(data.decode())

            if message.get("type") != "hello":
                return

            if message["connect_id"] == self.connect_id:
                return  # ignore self

            peer_info = {
                "connect_id": message["connect_id"],
                "ip": addr[0],
                "tcp_port": message["tcp_port"]
            }

            self.on_peer_discovered(peer_info)

        except Exception:
            pass
