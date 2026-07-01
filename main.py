import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from interface_grafica.configuration import ConfigurationBox 
from interface_grafica.rxBox import RxBox
from interface_grafica.txBox import TxBox
import sockets.server as server
import threading
import sockets.client as client

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Simulador de Redes")
        self.set_default_size(600, 750) 
        
        self.setupProperties()
        self.add(self.main_layout())

    def main_layout(self):
        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin=10
        )

        self.configBox = ConfigurationBox()
        self.configBox.set_on_start_callback(
            self.start_simulation_button
        )

        # Definindo as propriedades de expansão para a janela ficar fluida
        self.main_box.pack_start(self.configBox.setupConfiguration(), False, False, 0)
        self.main_box.pack_start(self.txBox.setupTx(), True, True, 0)
        self.main_box.pack_start(self.rxBox.setupRx(), True, True, 0)

        return self.main_box

    def start_simulation_button(self, config):
        self.txBox.update_configuration(config)
        self.rxBox.update_configuration(config)
        self.txBox.on_send_clicked()
        
    def setupProperties(self) -> None:
        self.servidor = server.Servidor()
        self.cliente = client.Cliente()
        
        self.txBox = TxBox(self.cliente)
        self.rxBox = RxBox(self.servidor)

        self.servidor.set_callback(
            self.rxBox.on_data_received
        )
        
        # O PULO DO GATO: Liga o receptor ao transmissor para a retransmissão automática
        self.rxBox.set_retransmit_callback(
            self.txBox.on_send_clicked
        )

        self.thServer = threading.Thread(target=self.servidor.start, daemon=True)
        self.thServer.start()

if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()