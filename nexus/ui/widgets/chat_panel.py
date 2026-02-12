from textual.containers import VerticalScroll
from textual.widgets import Static


class ChatPanel(VerticalScroll):

    def add_message(self, message):
        bubble = Static(
            f"{message.sender}: {message.content}",
            classes="message"
        )
        self.mount(bubble)
