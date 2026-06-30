import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

import sockets.server as server
from maquina_estados import maquina_estados
from codigo_fisica.camada_fisica import Canal  # Importando o meio físico

class RxBox:
    def __init__(self, servidor):
        self.config = {}
        self.servidor = servidor

        self.inputText = self.setupReceivedField()

        # Registra este RxBox para receber os dados
        self.servidor.set_callback(self.on_data_received)

    def setupReceivedField(self) -> Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("")
        textEntry.set_editable(False)
        return textEntry

    def setupRx(self) -> Gtk.Box:
        frame = Gtk.Frame(label="Receptor")

        box = Gtk.Box(spacing=6)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        box.pack_start(self.inputText, True, True, 0)
        frame.add(box)

        return frame

    def on_data_received(self, data):
        # Instanciamos o Meio de Comunicação (Canal)
        canal = Canal()
        
        # Resgatamos o valor do ruído (Sigma) configurado na interface
        sigma_ruido = self.config.get('sigma_ruido', 0.0)
        
        # O Meio Físico corrompe o array de tensões elétricas recebidas
        sinal_com_ruido = canal.adicionar_ruido(data, x=0.0, sigma=sigma_ruido)
        
        # A máquina de estados recebe o sinal já corrompido para tentar decodificar
        machine = maquina_estados.MaquinaEstados(self.config, msg='')
        mensagem = machine.receving(sinal_com_ruido)
        
        print(f"RX recebeu (Sigma={sigma_ruido}):", mensagem)

        # Atualização segura da interface gráfica usando a thread principal do GTK
        GLib.idle_add(self.inputText.set_text, mensagem)

    def update_configuration(self, config):
        self.config = config
        print(self.config)