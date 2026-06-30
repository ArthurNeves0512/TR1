import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
import sockets.server as server
from gi.repository import Gtk, GLib
from maquina_estados import maquina_estados

class RxBox:
    def __init__(self, servidor):
        self.config = {}
        self.servidor = servidor

        self.inputText = self.setupReceivedField()

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
    
    def safe_ui_text(self,msg):
        if msg is None:
            return ""

        if isinstance(msg, (bytes, bytearray)):
            msg = msg.decode("utf-8", errors="replace")

        if not isinstance(msg, str):
            msg = str(msg)

        return msg
    def update_ui(self, mensagem):
        self.inputText.set_text(mensagem)
        return False

    def on_data_received(self, data):
        machine = maquina_estados.MaquinaEstados(self.config,msg='')
        mensagem = machine.receving(data)
        print("RX recebeu:", mensagem)
        mensagem = self.safe_ui_text(mensagem)
        GLib.idle_add(self.update_ui, mensagem)

 
    

    def update_configuration(self, config):
        self.config = config
        print(self.config)