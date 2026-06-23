import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gi.repository import Gtk
from codigo_fisica import camada_fisica
from sockets import client

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

        # maquina_de_estados = camada_fisica()
        
        # mensagem_modularizada = maquina_de_estados.execute(self.config['digital_modulation'],msg=mensagem)

        print("TX enviando:", mensagem)

        self.cliente.send_message(
            mensage=mensagem
        )

    def update_configuration(self, config):
        self.config = config

        

    