import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ConfigurationBox:
    def __init__(self):
        self.config = {
            "modulation": "",
            "framming_type":"Contagem de Caracteres",
            "voltage_level":5,
            'detection_type':'',
            'frame_size':8,
            'media_ruido': 0.0,
            'sigma_ruido': 0.0
        }
        self.on_start_callback = None

        self.modulation_comboBox = self.setup_modulation_comboBox()
        self.start_simulation_button =self.startSimulationButton()
        self.voltageLevelInputText = self.setupVoltageLevelInputField()
        self.frameSizeInputText = self.setupFrameSizeInputField()
        self.noiseInputText = self.setupNoiseInputField()
        self.meanNoiseInputText = self.setupMeanNoiseInputField()
        self.detecting_correting_comboBox= self.setup_detecting_or_correcting_error_comboBox()
        self.framming_type_comboBox = self.setup_framming_type_comboBox()


    def set_on_start_callback(self,callback):
        self.on_start_callback=callback

    
    def setup_modulation_comboBox(self)->Gtk.ComboBoxText:
        modulation_comboBox = Gtk.ComboBoxText()
        modulation_comboBox.append_text("Nrz Polar")
        modulation_comboBox.append_text("Bipolar")
        modulation_comboBox.append_text("Manchester")
        modulation_comboBox.append_text("ASK")
        modulation_comboBox.append_text("FSK")
        modulation_comboBox.append_text("QPSK")
        modulation_comboBox.append_text("16-QAM")
        modulation_comboBox.set_active(0)
        self.config['modulation']="Nrz Polar"
        modulation_comboBox.connect("changed",self.setModulation)
        return modulation_comboBox
    
    def setup_detecting_or_correcting_error_comboBox(self)->Gtk.ComboBoxText:
        digital_modulation_comboBox = Gtk.ComboBoxText()
        digital_modulation_comboBox.append_text("Paridade")
        digital_modulation_comboBox.append_text("CheckSum")
        digital_modulation_comboBox.append_text("CRC")
        digital_modulation_comboBox.append_text("Hamming")
        digital_modulation_comboBox.set_active(0)
        self.config['detection_type']="Paridade"
        digital_modulation_comboBox.connect("changed",self.set_detecting_or_correcting_error)
        return digital_modulation_comboBox

    def setModulation(self, widget):
        self.config["modulation"] = widget.get_active_text()
        print(self.config["modulation"])
    
    def set_detecting_or_correcting_error(self,widget):
        self.config["detection_type"] = widget.get_active_text()        
        print(self.config['detection_type'])

    def setup_framming_type_comboBox(self)->Gtk.ComboBoxText:
        digital_modulation_comboBox = Gtk.ComboBoxText()
        digital_modulation_comboBox.append_text("Contagem de Caracteres")
        digital_modulation_comboBox.append_text("Inserção Bytes")
        digital_modulation_comboBox.append_text("Inserção Bits")
        digital_modulation_comboBox.set_active(0)
        digital_modulation_comboBox.connect("changed",self.setFrammingType)
        return digital_modulation_comboBox
    
    def setFrammingType(self,widget):
        self.config["framming_type"] = widget.get_active_text()
        print(self.config["framming_type"])


    def startSimulationButton(self)->Gtk.Button:
        startButton = Gtk.Button(label="Start Simulation")
        startButton.connect("clicked",self.start_button_callback_trigger)
        return startButton

    def start_button_callback_trigger(self, button):
        if self.on_start_callback:
            # Captura os valores digitados nas caixas de texto
            self.config['voltage_level'] = int(self.voltageLevelInputText.get_text())
            self.config['frame_size'] = int(self.frameSizeInputText.get_text())
            self.config['sigma_ruido'] = float(self.noiseInputText.get_text())
            self.config['media_ruido'] = float(self.meanNoiseInputText.get_text())

            self.on_start_callback(self.config.copy())
            
    def setupVoltageLevelInputField(self) -> Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("5")
        return textEntry


    def setupFrameSizeInputField(self)->Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("8")
        return textEntry
    
    def setupNoiseInputField(self) -> Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("0.0")  # Valor padrão inicializado para ruido sigma
        return textEntry

    def setupMeanNoiseInputField(self) -> Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("0.0")  # Valor padrão inicializado para ruido media
        return textEntry

    def setupConfiguration(self)->Gtk.Box:
        box = Gtk.Box(spacing=6)
        box.pack_start(self.modulation_comboBox,True,True,0)
        box.pack_start(self.voltageLevelInputText,True,True,0)
        box.pack_start(self.frameSizeInputText,True,True,0)
        box.pack_start(self.noiseInputText,True,True,0)
        box.pack_start(self.meanNoiseInputText,True,True,0)
        box.pack_start(self.detecting_correting_comboBox,True,True,0)
        box.pack_start(self.framming_type_comboBox,True,True,0)
        box.pack_start(self.start_simulation_button,True,True,0)
        
        return box
    
    