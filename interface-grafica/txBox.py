import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class TxBox:
    def __init__(self):

        self.config = {}
        self.inputText=self.setupInputField()


    def setupInputField(self)->Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("A")
        return textEntry

    
    def setupTx(self)->Gtk.Box:
        box = Gtk.Box(spacing=6)
        box.pack_start(self.inputText,True,True,0)
        return box

    def update_configuration(self,config):
        self.config = config

        

    