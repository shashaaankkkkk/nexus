import asyncio

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Static

from nexus.ui.widgets.sidebar import Sidebar
from nexus.ui.widgets.chat_panel import ChatPanel
from nexus.ui.widgets.input_bar import InputBar

from nexus.core.identity import Identity
from nexus.core.storage import Storage
from nexus.core.models import Message

from nexus.core.network.discovery import DiscoveryService
from nexus.core.network.tcp_server import TCPServer
from nexus.core.network.connection import Connection


class NexusApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("ctrl+d", "toggle_debug", "Toggle Debug"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    debug_visible = reactive(False)

    async def on_mount(self) -> None:
        # ----------------------------
        # Identity & Storage
        # ----------------------------
        self.identity = Identity.load_or_create()
        self.storage = Storage()

        # Cache UI references
        self.sidebar = self.query_one("#sidebar", Sidebar)
        self.chat_panel = self.query_one("#chat-panel", ChatPanel)

        # Display ConnectID
        self.sidebar.mount(
            Static(
                f"ID: {self.identity.connect_id}",
                id="connect-id"
            )
        )

        # Load stored messages
        for data in self.storage.load_messages():
            try:
                message = Message.from_dict(data)
                self.chat_panel.add_message(message)
            except Exception:
                continue

        # ----------------------------
        # Peer Tracking
        # ----------------------------
        self.peers = {}

        # ----------------------------
        # TCP SERVER (Incoming Connections)
        # ----------------------------
        async def handle_client(reader, writer):
            connection = Connection(reader, writer)
            await connection.perform_handshake(self.identity.connect_id)

            print(f"Incoming connection from {connection.peer_id}")

        self.tcp_server = TCPServer(
            host="0.0.0.0",
            port=10000,
            on_client_connected=handle_client
        )

        await self.tcp_server.start()

        # ----------------------------
        # DISCOVERY (UDP Broadcast)
        # ----------------------------
        async def handle_peer(peer_info):
            peer_id = peer_info["connect_id"]

            if peer_id in self.peers:
                return

            self.peers[peer_id] = peer_info
            print(f"Discovered peer: {peer_info}")

            # Deterministic connection rule
            if self.identity.connect_id < peer_id:
                try:
                    reader, writer = await asyncio.open_connection(
                        peer_info["ip"],
                        peer_info["tcp_port"]
                    )

                    connection = Connection(reader, writer)
                    await connection.perform_handshake(
                        self.identity.connect_id
                    )

                    print(f"Connected to {connection.peer_id}")

                except Exception as e:
                    print(f"Connection failed: {e}")

        def discovery_callback(peer_info):
            asyncio.create_task(handle_peer(peer_info))

        self.discovery = DiscoveryService(
            connect_id=self.identity.connect_id,
            tcp_port=10000,
            on_peer_discovered=discovery_callback
        )

        asyncio.create_task(self.discovery.start())

    # ----------------------------
    # UI Layout
    # ----------------------------
    def compose(self) -> ComposeResult:
        with Horizontal(id="main-layout"):
            yield Sidebar(id="sidebar")
            yield ChatPanel(id="chat-panel")

        yield InputBar(id="input-bar")

    # ----------------------------
    # Send Button (Local Only)
    # ----------------------------
    def on_button_pressed(self, event) -> None:
        if event.button.id == "send-btn":
            input_widget = self.query_one("#message-input")

            content = input_widget.value.strip()
            if not content:
                return

            message = Message.create(
                sender=self.identity.connect_id,
                content=content
            )

            self.storage.save_message(message)
            self.chat_panel.add_message(message)

            input_widget.value = ""
