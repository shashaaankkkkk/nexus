from textual.containers import Horizontal
from textual.widgets import Input, Button


class InputBar(Horizontal):
    def compose(self):
        yield Input(placeholder="Type a message...", id="message-input")
        yield Button("Send", id="send-btn")
