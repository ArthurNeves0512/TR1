import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gi.repository import Gtk
from camada_fisica import camada_fisica

class TxBox:
    def __init__(self, cliente):
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


        maquina_de_estados = camada_fisica.MaquinaDeEstados()
        
        mensagem_modularizada = maquina_de_estados.execute(self.config['digital_modulation'],msg=mensagem)

        print("TX enviando:", mensagem_modularizada)

        self.cliente.send_message(
            message=mensagem_modularizada
        )

    def update_configuration(self, config):
        self.config = config

        

    