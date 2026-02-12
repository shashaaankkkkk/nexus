from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Static
from nexus.ui.widgets.sidebar import Sidebar
from nexus.ui.widgets.chat_panel import ChatPanel
from nexus.ui.widgets.input_bar import InputBar
from nexus.core.identity import Identity
from nexus.core.storage import Storage
import time


class NexusApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("ctrl+d", "toggle_debug", "Toggle Debug"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    debug_visible = reactive(False)

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-layout"):
            yield Sidebar(id="sidebar")
            yield ChatPanel(id="chat-panel")

        yield InputBar(id="input-bar")

    def on_button_pressed(self, event):
        if event.button.id == "send-btn":
            input_widget = self.query_one("#message-input")
            chat = self.query_one("#chat-panel")

            content = input_widget.value.strip()
            if content:
                message_id = f"{self.identity.connect_id}-{int(time.time())}"

                self.storage.save_message(
                    message_id,
                    self.identity.connect_id,
                    content
                )

                chat.add_message(content)
                input_widget.value = ""


    def on_mount(self) -> None:
        self.identity = Identity.load_or_create()
        sidebar = self.query_one("#sidebar")
        sidebar.mount(
            Static(f"ID: {self.identity.connect_id}", id="connect-id")
        )
        self.storage = Storage()
        # Load existing messages
        chat = self.query_one("#chat-panel")
        for row in self.storage.load_messages():
            chat.add_message(row["content"])


