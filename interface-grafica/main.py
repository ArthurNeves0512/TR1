import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import configuration as configWindows
class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Interface Gráfica com GTK")
        self.config = configWindows.ConfigurationBox()
        button = Gtk.Button(label="Clique aqui")
        button.connect("clicked", self.on_button_clicked)
        self.add(self.config.digital_comboBox)

    def on_button_clicked(self, widget):
        print("O botão foi clicado!")


if __name__ == "__main__":

    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
