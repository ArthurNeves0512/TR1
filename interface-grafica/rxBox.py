import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class RxBox:
    def __init__(self):
        self.config = {
            "receivedText": "",
            "receivedTextDigitalModulation":0,
            "receivedTextAnalogModulation":0
        }
        self.inputText=self.setupReceivedField()

    
    def setupReceivedField(self)->Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("")
        textEntry.set_editable(False)
        return textEntry

    
    def setupRx(self)->Gtk.Box:
        box = Gtk.Box(spacing=6)
        box.pack_start(self.inputText,True,True,0)
        return box
