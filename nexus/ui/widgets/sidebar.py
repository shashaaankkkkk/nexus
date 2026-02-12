from textual.containers import Vertical
from textual.widgets import Static


class Sidebar(Vertical):
    def compose(self):
        yield Static("NEXUS", id="logo")
        yield Static("Status: Offline", id="status")
        yield Static("Contacts", id="contacts-header")
