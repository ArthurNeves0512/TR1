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

        self.main_box.pack_start(configWindows.ConfigurationBox().setupConfiguration(),True,True,0)
        self.main_box.pack_start(txWindows.TxBox().setupTx(),True,True,0)
        self.main_box.pack_start(rxWindows.RxBox().setupRx(),True,True,0)
        
        return self.main_box


if __name__ == "__main__":

    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
