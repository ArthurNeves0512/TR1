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
        super().__init__(title="Simulador de redes")

        self.setupProperties()
        self.add(self.main_layout())

    def main_layout(self):
        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )

        self.configBox = ConfigurationBox()
        self.configBox.set_on_start_callback(
            self.start_simulation_button
        )

        self.main_box.pack_start(
            self.configBox.setupConfiguration(),
            True, True, 0
        )

        self.main_box.pack_start(
            self.txBox.setupTx(),
            True, True, 0
        )

        self.main_box.pack_start(
            self.rxBox.setupRx(),
            True, True, 0
        )

        return self.main_box


    def start_simulation_button(self,config):
        self.txBox.update_configuration(config)
        self.rxBox.update_configuration(config)
        self.txBox.on_send_clicked(self)
        
        
    def setupProperties(self)->None:
        self.servidor = server.Servidor()
        self.cliente = client.Cliente()
        
        self.txBox = TxBox(self.cliente)

        self.rxBox = RxBox(self.servidor)

        self.servidor.set_callback(
            self.rxBox.on_data_received
        )

        self.thServer = threading.Thread(target=self.servidor.start,
                          daemon=True)
        self.thServer.start()


if __name__ == "__main__":



    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
