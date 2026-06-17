import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import configuration as configWindows
import txBox as txWindows
import rxBox as rxWindows
class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Simulador de redes")
        self.add(self.main_layout())




    def main_layout(self)->Gtk.Box:
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        self.configBox = configWindows.ConfigurationBox()
        self.configBox.set_on_start_callback(self.start_simulation_button)
        self.txBox = txWindows.TxBox()
        self.rxBox = rxWindows.RxBox()

        self.main_box.pack_start(self.configBox.setupConfiguration(),True,True,0)
        self.main_box.pack_start(self.txBox.setupTx(),True,True,0)
        self.main_box.pack_start(self.rxBox.setupRx(),True,True,0)
        return self.main_box


    def start_simulation_button(self,config):
        self.txBox.update_configuration(config)
        self.rxBox.update_configuration(config)

if __name__ == "__main__":

    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
