import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gi.repository import Gtk
from codigo_fisica import camada_fisica
from sockets import client
from maquina_estados import maquina_estados

class TxBox:
    def __init__(self, cliente:client.Cliente):
        self.cliente = cliente

        self.config = {}
        self.inputText = self.setupInputField()

    def setupInputField(self) -> Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("A")
        return textEntry

    def setupTx(self) -> Gtk.Box:
        box = Gtk.Box(spacing=6)

        box.pack_start(self.inputText, True, True, 0)

        return box

    def on_send_clicked(self, button):

        mensagem = self.inputText.get_text()
        converter_bits = maquina_estados.BitConverter()
        mensagem = converter_bits.text_to_bits(mensagem)
        state_machine = maquina_estados.MaquinaEstados(self.config,mensagem)
        b = state_machine.execute()
        print("mensagem:", mensagem)
        print("TX enviando:", b)

        self.cliente.send_message(
            array=b
        )

    def update_configuration(self, config):
        self.config = config

        

    