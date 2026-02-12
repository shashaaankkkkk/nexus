from textual.containers import VerticalScroll
from textual.widgets import Static


class ChatPanel(VerticalScroll):
    def add_message(self, content: str) -> None:
        self.mount(Static(content, classes="message"))
