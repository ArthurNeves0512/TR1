import gi
import sys
gi.require_version("Gtk", "4.0")
gi.require_version("Adw",'1')
from gi.repository import  Gtk,Adw


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self,*agrs,**kwargs):
        super().__init__(*agrs,**kwargs)
       
        self.set_default_size(800,400)
        self.set_title("Simulador de Comunicação Digital")

        self.configurationHeaderBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.configurationHeaderBox)

        self.initButton = Gtk.Button(label="Iniciar Simulação")
        self.configurationHeaderBox.append(self.initButton)
        self.initButton.connect("clicked",self.print)

        self.resetButton = Gtk.Button(label="Resetar")
        self.configurationHeaderBox.append(self.resetButton)
        self.resetButton.connect("clicked",self.print)
        

    
    
    def print(self,button):
        print("UHUUUUU")

class MyApp(Adw.Application):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.connect('activate',self.on_active)


    def on_active(self,app):
        self.win = MainWindow(application=app)
        self.win.present()



app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)
