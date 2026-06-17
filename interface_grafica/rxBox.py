import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
import server as server
from gi.repository import Gtk, GLib


class RxBox:
    def __init__(self, servidor):
        self.config = {}
        self.servidor = servidor

        self.inputText = self.setupReceivedField()

        # registra este RxBox para receber os dados
        self.servidor.set_callback(self.on_data_received)

    def setupReceivedField(self) -> Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("")
        textEntry.set_editable(False)
        return textEntry

    def setupRx(self) -> Gtk.Box:
        box = Gtk.Box(spacing=6)
        box.pack_start(self.inputText, True, True, 0)
        return box

    def on_data_received(self, data):
        mensagem = data.decode()

        print("RX recebeu:", mensagem)

        GLib.idle_add(
            self.inputText.set_text,
            mensagem
        )

    def update_configuration(self, config):
        self.config = config
        print(self.config)