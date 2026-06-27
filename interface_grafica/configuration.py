import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ConfigurationBox:
    def __init__(self):
        self.config = {
            "digital_modulation": "",
            "analog_modulation":"",
            "voltage_level":10,
            'detect_correct':'',
            'frame_size':8
        }
        self.on_start_callback = None

        self.digital_comboBox = self.setup_digital_modulation_comboBox()
        self.analog_comboBox = self.setup_analog_modulation_comboBox()
        self.start_simulation_button =self.startSimulationButton()
        self.voltageLevelInputText = self.setupVoltageLevelInputField()
        self.frameSizeInputText = self.setupFrameSizeInputField()
        self.detecting_correting_comboBox= self.setup_detecting_or_correcting_error_comboBox()



    def set_on_start_callback(self,callback):
        self.on_start_callback=callback


    
    def setup_digital_modulation_comboBox(self)->Gtk.ComboBoxText:
        digital_modulation_comboBox = Gtk.ComboBoxText()
        digital_modulation_comboBox.append_text("Nrz Polar")
        digital_modulation_comboBox.append_text("Bipolar")
        digital_modulation_comboBox.append_text("Manchester")
        digital_modulation_comboBox.set_active(0)
        self.config['digital_modulation']="Nrz Polar"
        digital_modulation_comboBox.connect("changed",self.setDigitalModulation)
        return digital_modulation_comboBox
    
    def setup_detecting_or_correcting_error_comboBox(self)->Gtk.ComboBoxText:
        digital_modulation_comboBox = Gtk.ComboBoxText()
        digital_modulation_comboBox.append_text("Paridade")
        digital_modulation_comboBox.append_text("CheckSum")
        digital_modulation_comboBox.append_text("CRC")
        digital_modulation_comboBox.append_text("Hamming")
        digital_modulation_comboBox.set_active(0)
        self.config['detect_correct']="Paridade"
        digital_modulation_comboBox.connect("changed",self.set_detecting_or_correcting_error)
        return digital_modulation_comboBox
    
    def setup_analog_modulation_comboBox(self)->Gtk.ComboBoxText:
        analog_modulation_comboBox = Gtk.ComboBoxText()
        analog_modulation_comboBox.append_text("ASK")
        analog_modulation_comboBox.append_text("FSK")
        analog_modulation_comboBox.append_text("PSK")
        analog_modulation_comboBox.append_text("QPSK")
        analog_modulation_comboBox.append_text("16-QAM")
        analog_modulation_comboBox.set_active(0)
        self.config['analog_modulation']="ASK"
        analog_modulation_comboBox.connect("changed",self.setAnalogModulation)
        return analog_modulation_comboBox


    def setDigitalModulation(self, widget):
        self.config["digital_modulation"] = widget.get_active_text()
        print(self.config["digital_modulation"])

    def setAnalogModulation(self,widget):
        self.config["analog_modulation"]=widget.get_active_text()
        print(self.config['analog_modulation'])
    
    def set_detecting_or_correcting_error(self,widget):
        self.config["detect_correct"] = widget.get_active_text()
        print(self.config['detect_correct'])

    def startSimulationButton(self)->Gtk.Button:
        startButton = Gtk.Button(label="Start Simulation")
        startButton.connect("clicked",self.start_button_callback_trigger)
        return startButton

    def start_button_callback_trigger(self,button):
        if self.on_start_callback:
            if(self.voltageLevelInputText.get_text()!='Nivel de Tensão'):
                self.config['voltage_level']=int(self.voltageLevelInputText.get_text())
            if(self.frameSizeInputText.get_text()!='Tamanho do quadro'):
                self.config['frame_size']=int(self.frameSizeInputText.get_text())
            self.on_start_callback(self.config.copy())
            
    def setupVoltageLevelInputField(self) -> Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("Nivel de Tensão")
        return textEntry


    def setupFrameSizeInputField(self)->Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("Tamanho do quadro")
        return textEntry
    
    def setupConfiguration(self)->Gtk.Box:
        box = Gtk.Box(spacing=6)
        box.pack_start(self.digital_comboBox,True,True,0)
        box.pack_start(self.analog_comboBox,True,True,0)
        box.pack_start(self.voltageLevelInputText,True,True,0)
        box.pack_start(self.frameSizeInputText,True,True,0)
        box.pack_start(self.detecting_correting_comboBox,True,True,0)

        box.pack_start(self.start_simulation_button,True,True,0)
        
        return box
    
    