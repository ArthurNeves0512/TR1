import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ConfigurationBox:
    def __init__(self):
        self.config = {
            "digital_modulation": ""
        }
        self.digital_comboBox = self.setup_digital_modulation_comboBox()

    def setup_digital_modulation_comboBox(self)->Gtk.ComboBoxText:
        self.digital_modulation_comboBox = Gtk.ComboBoxText()
        self.digital_modulation_comboBox.append_text("Nrz Polar")
        self.digital_modulation_comboBox.append_text("Bipolar")
        self.digital_modulation_comboBox.append_text("Manchester")
        self.digital_modulation_comboBox.set_active(0)
        self.digital_modulation_comboBox.connect("changed",self.printa)
        return self.digital_modulation_comboBox
    
    def printa(self, widget):
        self.config["digital_modulation"] = widget.get_active_text()
        print(self.config["digital_modulation"])

        