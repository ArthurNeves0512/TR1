import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ConfigurationBox:
    def __init__(self):
        self.config = {
            "modulation": "",
            "framming_type":"Contagem de Caracteres",
            "voltage_level":10,
            'detection_type':'',
            'media_erro':0.0,
            'sigma_erro':0.0,
            'frame_size':1
        }
        self.on_start_callback = None

        self.modulation_comboBox = self.setup_modulation_comboBox()
        self.start_simulation_button =self.startSimulationButton()
        self.voltageLevelInputText = self.setupVoltageLevelInputField()
        self.frameSizeInputText = self.setupFrameSizeInputField()
        self.mediaErrorInputText = self.setupMediaErrorInput()
        self.sigmaErrorInputText = self.setupSigmaErrorInput()
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
        self.config["detect_correct"] = widget.get_active_text()
        print(self.config['detect_correct'])

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

    def start_button_callback_trigger(self,button):
        if self.on_start_callback:
            if(self.voltageLevelInputText.get_text()!='Nivel de Tensão'):
                self.config['voltage_level']=int(self.voltageLevelInputText.get_text())
            if(self.frameSizeInputText.get_text()!='Tamanho do quadro'):
                self.config['frame_size']=int(self.frameSizeInputText.get_text())
            if(self.mediaErrorInputText.get_text()!='Nivel de media pro erro'):
                self.config['media_erro']=float(self.mediaErrorInputText.get_text())
            if(self.sigmaErrorInputText.get_text()!='Tamanho do quadro'):
                self.config['sigma_erro']=float(self.sigmaErrorInputText.get_text())
            self.on_start_callback(self.config.copy())
            
    def setupVoltageLevelInputField(self) -> Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("Nivel de Tensão")
        return textEntry
    
    def setupMediaErrorInput(self) -> Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("Nivel de media pro erro")
        return textEntry
    
    def setupSigmaErrorInput(self) -> Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("Nivel de sigma pro erro")
        return textEntry

    def setupFrameSizeInputField(self)->Gtk.Entry:
        textEntry = Gtk.Entry()
        textEntry.set_text("Tamanho do quadro")
        return textEntry
    
    def setupConfiguration(self)->Gtk.Box:
        box = Gtk.Box(spacing=6)
        box.pack_start(self.modulation_comboBox,True,True,0)
        box.pack_start(self.voltageLevelInputText,True,True,0)
        box.pack_start(self.frameSizeInputText,True,True,0)
        box.pack_start(self.mediaErrorInputText,True,True,0)
        box.pack_start(self.sigmaErrorInputText,True,True,0)
        box.pack_start(self.detecting_correting_comboBox,True,True,0)
        box.pack_start(self.framming_type_comboBox,True,True,0)
        box.pack_start(self.start_simulation_button,True,True,0)
        
        return box
    
    