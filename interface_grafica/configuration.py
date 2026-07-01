import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ConfigurationBox:
    def __init__(self):
        self.config = {
            "modulation": "Nrz Polar",
            "framming_type": "Contagem de Caracteres",
            "error_control": "Paridade Par",
            "voltage_level": 5,
            "media_erro": 0.0,
            "sigma_erro": 0.0,
            "frame_size": 4,
        }
        self.on_start_callback = None

        self.digital_mod_comboBox = self.setup_digital_modulation()
        self.analog_mod_comboBox = self.setup_analog_modulation()
        self.framming_type_comboBox = self.setup_framming_type_comboBox()
        self.detecting_correting_comboBox = self.setup_detecting_or_correcting_error_comboBox()

        self.voltageLevelInputText = Gtk.Entry(text="5")
        self.frameSizeInputText = Gtk.Entry(text="4")
        self.mediaErrorInputText = Gtk.Entry(text="0.0")
        self.sigmaErrorInputText = Gtk.Entry(text="0.0")

        self.start_simulation_button = Gtk.Button(label="Iniciar Simulação (Tx)")
        self.start_simulation_button.connect("clicked", self.start_button_callback_trigger)

    def set_on_start_callback(self, callback):
        self.on_start_callback = callback

    def setup_digital_modulation(self) -> Gtk.ComboBoxText:
        cb = Gtk.ComboBoxText()
        for m in ["Nrz Polar", "Bipolar", "Manchester"]:
            cb.append_text(m)
        cb.set_active(0)
        cb.connect("changed", self.update_modulation)
        return cb

    def setup_analog_modulation(self) -> Gtk.ComboBoxText:
        cb = Gtk.ComboBoxText()
        cb.append_text("Nenhuma (Usar Digital)")
        for m in ["ASK", "FSK", "QPSK", "16-QAM"]:
            cb.append_text(m)
        cb.set_active(0)
        cb.connect("changed", self.update_modulation)
        return cb

    def update_modulation(self, widget):
        analog_val = self.analog_mod_comboBox.get_active_text()
        if analog_val and analog_val != "Nenhuma (Usar Digital)":
            self.config["modulation"] = analog_val
        else:
            self.config["modulation"] = self.digital_mod_comboBox.get_active_text()
        print("Modulação definida no Config:", self.config["modulation"])

    def setup_detecting_or_correcting_error_comboBox(self) -> Gtk.ComboBoxText:
        cb = Gtk.ComboBoxText()
        for e in ["Paridade Par", "Checksum", "CRC-32", "Hamming"]:
            cb.append_text(e)
        cb.set_active(0)
        cb.connect("changed", self.set_detecting_or_correcting_error)
        return cb

    def set_detecting_or_correcting_error(self, widget):
        self.config["error_control"] = widget.get_active_text()
        print("Controle de erro definido:", self.config["error_control"])

    def setup_framming_type_comboBox(self) -> Gtk.ComboBoxText:
        cb = Gtk.ComboBoxText()
        for f in ["Contagem de Caracteres", "Inserção Bytes", "Inserção Bits"]:
            cb.append_text(f)
        cb.set_active(0)
        cb.connect("changed", self.setFrammingType)
        return cb

    def setFrammingType(self, widget):
        self.config["framming_type"] = widget.get_active_text()
        print("Enquadramento definido:", self.config["framming_type"])

    def _mostrar_erro(self, mensagem):
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Configuração inválida",
        )
        dialog.format_secondary_text(mensagem)
        dialog.run()
        dialog.destroy()

    def _validar_tamanho_quadro(self, tamanho):
        metodo = self.config["framming_type"]

        if tamanho <= 0:
            raise ValueError("O tamanho do quadro deve ser maior que zero.")

        if metodo == "Contagem de Caracteres":
            if tamanho < 2:
                raise ValueError(
                    "Na contagem de caracteres, o quadro precisa ter pelo menos 2 bytes."
                )
            if tamanho > 255:
                raise ValueError(
                    "Na contagem de caracteres, o quadro pode ter no máximo 255 bytes."
                )

        elif metodo == "Inserção Bytes" and tamanho < 4:
            raise ValueError(
                "Na inserção de bytes, use pelo menos 4 bytes por quadro."
            )

        elif metodo == "Inserção Bits" and tamanho < 3:
            raise ValueError(
                "Na inserção de bits, use pelo menos 3 bytes por quadro."
            )

    def start_button_callback_trigger(self, button):
        if not self.on_start_callback:
            return

        try:
            self.config["voltage_level"] = int(self.voltageLevelInputText.get_text())
            self.config["frame_size"] = int(self.frameSizeInputText.get_text())
            self.config["media_erro"] = float(self.mediaErrorInputText.get_text())
            self.config["sigma_erro"] = float(self.sigmaErrorInputText.get_text())

            if self.config["voltage_level"] <= 0:
                raise ValueError("A tensão deve ser maior que zero.")
            if self.config["media_erro"] < 0 or self.config["sigma_erro"] < 0:
                raise ValueError("Os valores de ruído não podem ser negativos.")

            self._validar_tamanho_quadro(self.config["frame_size"])

        except ValueError as erro:
            self._mostrar_erro(str(erro))
            return

        self.on_start_callback(self.config.copy())

    def setupConfiguration(self) -> Gtk.Frame:
        # Mantém o mesmo formato visual original.
        frame = Gtk.Frame(label="Configurações Gerais")
        grid = Gtk.Grid(column_spacing=15, row_spacing=10, margin=10)

        grid.attach(Gtk.Label(label="Modulação Digital:"), 0, 0, 1, 1)
        grid.attach(self.digital_mod_comboBox, 1, 0, 1, 1)

        grid.attach(Gtk.Label(label="Modulação Analógica:"), 0, 1, 1, 1)
        grid.attach(self.analog_mod_comboBox, 1, 1, 1, 1)

        grid.attach(Gtk.Label(label="Enquadramento:"), 0, 2, 1, 1)
        grid.attach(self.framming_type_comboBox, 1, 2, 1, 1)

        grid.attach(Gtk.Label(label="Detecção/Correção de Erros:"), 0, 3, 1, 1)
        grid.attach(self.detecting_correting_comboBox, 1, 3, 1, 1)

        grid.attach(Gtk.Label(label="Tensão:"), 2, 0, 1, 1)
        grid.attach(self.voltageLevelInputText, 3, 0, 1, 1)

        grid.attach(Gtk.Label(label="Tamanho do Quadro:"), 2, 1, 1, 1)
        grid.attach(self.frameSizeInputText, 3, 1, 1, 1)

        grid.attach(Gtk.Label(label="Ruído Média(x):"), 2, 2, 1, 1)
        grid.attach(self.mediaErrorInputText, 3, 2, 1, 1)

        grid.attach(Gtk.Label(label="Ruído Sigma(σ):"), 2, 3, 1, 1)
        grid.attach(self.sigmaErrorInputText, 3, 3, 1, 1)

        grid.attach(self.start_simulation_button, 0, 4, 4, 1)

        frame.add(grid)
        return frame
