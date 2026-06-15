import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class TxBox:
    def __init__(self):
        self.config = {
            "inputText": "",
            "outputTextDigitalModulation":0,
            "outputTextAnalogModulation":0
        }
        self.inputText=self.setupInputField()

    

    def setupInputField(self)->Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("A")
        return textEntry

    
    def setupTx(self)->Gtk.Box:
        box = Gtk.Box(spacing=6)
        box.pack_start(self.inputText,True,True,0)
        return box


        

    