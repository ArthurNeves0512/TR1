import gi
import server
import client
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        
        super().__init__(application=app)

        self.set_title("Simulador de Comunicação Digital")
        self.set_default_size(1600, 1000)

        self.server = server.Servidor()
        self.client = client.Cliente()
        self.string_tx=""
        self.string_rx=""
        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )

        self.set_child(self.main_box)

        self.create_configuration_area()
        self.create_center_area()
        self.create_bottom_area()

    # --------------------------------------------------
    # CONFIGURAÇÃO GERAL
    # --------------------------------------------------

    def create_configuration_area(self):
        frame = Gtk.Frame(label="CONFIGURAÇÃO GERAL")

        grid = Gtk.Grid(
            column_spacing=15,
            row_spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )

        frame.set_child(grid)

        # Tamanho quadro
        grid.attach(Gtk.Label(label="Tamanho máximo de quadro"), 0, 0, 1, 1)

        self.frame_size = Gtk.Entry()
        self.frame_size.set_text("1024")
        grid.attach(self.frame_size, 0, 1, 1, 1)

        # CRC
        grid.attach(Gtk.Label(label="Tamanho do EDC"), 1, 0, 1, 1)

        self.crc_combo = Gtk.ComboBoxText()
        self.crc_combo.append_text("CRC-16")
        self.crc_combo.append_text("CRC-32")
        self.crc_combo.set_active(0)

        grid.attach(self.crc_combo, 1, 1, 1, 1)

        # Enquadramento
        grid.attach(Gtk.Label(label="Tipo de enquadramento"), 2, 0, 1, 1)

        self.frame_combo = Gtk.ComboBoxText()
        self.frame_combo.append_text("Inserção de bytes")
        self.frame_combo.append_text("Inserção de bits")
        self.frame_combo.set_active(0)

        grid.attach(self.frame_combo, 2, 1, 1, 1)

        # Detecção
        grid.attach(Gtk.Label(label="Tipo de detecção"), 3, 0, 1, 1)

        self.edc_combo = Gtk.ComboBoxText()
        self.edc_combo.append_text("Detecção e correção (CRC)")
        self.edc_combo.set_active(0)

        grid.attach(self.edc_combo, 3, 1, 1, 1)

        # Modulação digital
        grid.attach(Gtk.Label(label="Modulação digital"), 4, 0, 1, 1)

        self.digital_combo = Gtk.ComboBoxText()
        self.digital_combo.append_text("NRZ")
        self.digital_combo.append_text("Manchester")
        self.digital_combo.set_active(0)

        grid.attach(self.digital_combo, 4, 1, 1, 1)

        # Modulação analógica
        grid.attach(Gtk.Label(label="Modulação analógica"), 5, 0, 1, 1)

        self.analog_combo = Gtk.ComboBoxText()
        self.analog_combo.append_text("ASK")
        self.analog_combo.append_text("FSK")
        self.analog_combo.append_text("PSK")
        self.analog_combo.set_active(0)

        grid.attach(self.analog_combo, 5, 1, 1, 1)

        # Ruído
        grid.attach(Gtk.Label(label="μ"), 6, 0, 1, 1)
        self.mu_entry = Gtk.Entry()
        self.mu_entry.set_text("0.0")
        grid.attach(self.mu_entry, 6, 1, 1, 1)

        grid.attach(Gtk.Label(label="σ"), 7, 0, 1, 1)
        self.sigma_entry = Gtk.Entry()
        self.sigma_entry.set_text("0.10")
        grid.attach(self.sigma_entry, 7, 1, 1, 1)

        start_btn = Gtk.Button(label="▶ Iniciar Simulação")
        grid.attach(start_btn, 8, 0, 1, 2)
        start_btn.connect("clicked",self.send_to_rx)

        self.main_box.append(frame)

    # --------------------------------------------------
    # ÁREA CENTRAL
    # --------------------------------------------------

    def send_to_rx(self,_button):
        self.client.send_message(message=self.string_tx)
        
    def create_center_area(self):

        center = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            homogeneous=True,
        )

        center.append(self.create_tx_panel())
        center.append(self.create_channel_panel())
        center.append(self.create_rx_panel())

        self.main_box.append(center)

    # --------------------------------------------------
    # TRANSMISSOR
    # --------------------------------------------------

    def create_tx_panel(self):

        frame = Gtk.Frame(label="TRANSMISSOR (TX)")

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )

        frame.set_child(box)

        # Aplicação
        app_frame = Gtk.Frame(label="1. APLICAÇÃO DE REDE")

        text = Gtk.TextView()
        text.get_buffer().set_text(
                "Olá, este é um exemplo de comunicação digital!"
        )

        self.string_tx=text.get_buffer().props.text

        app_frame.set_child(text)

        box.append(app_frame)

        # Enlace
        link_frame = Gtk.Frame(label="2. CAMADA DE ENLACE")

        link_text = Gtk.TextView()
        link_frame.set_child(link_text)

        box.append(link_frame)

        # Física
        phy_frame = Gtk.Frame(label="3. CAMADA FÍSICA (TX)")

        phy_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=5
        )

        phy_box.append(Gtk.Label(label="Sinal codificado (NRZ)"))
        phy_box.append(Gtk.DrawingArea(height_request=80))

        phy_box.append(Gtk.Label(label="Sinal modulado (ASK)"))
        phy_box.append(Gtk.DrawingArea(height_request=80))

        phy_frame.set_child(phy_box)

        box.append(phy_frame)

        return frame

    # --------------------------------------------------
    # CANAL
    # --------------------------------------------------

    def create_channel_panel(self):

        frame = Gtk.Frame(label="CANAL DE COMUNICAÇÃO")

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )

        frame.set_child(box)

        box.append(Gtk.Label(label="Sinal transmitido"))
        box.append(Gtk.DrawingArea(height_request=150))

        box.append(Gtk.Label(label="Sinal após ruído"))
        box.append(Gtk.DrawingArea(height_request=150))

        box.append(Gtk.Label(label="Comparação TX x RX"))
        box.append(Gtk.DrawingArea(height_request=200))

        return frame

    # --------------------------------------------------
    # RECEPTOR
    # --------------------------------------------------

    def create_rx_panel(self):

        frame = Gtk.Frame(label="RECEPTOR (RX)")

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )

        frame.set_child(box)

        phy_frame = Gtk.Frame(label="1. CAMADA FÍSICA (RX)")
        phy_frame.set_child(Gtk.DrawingArea(height_request=180))
        box.append(phy_frame)

        link_frame = Gtk.Frame(label="2. CAMADA DE ENLACE (RX)")
        link_frame.set_child(Gtk.TextView())
        box.append(link_frame)

        app_frame = Gtk.Frame(label="3. APLICAÇÃO DE REDE (RX)")
        app_frame.set_child(Gtk.TextView())
        box.append(app_frame)

        return frame

    # --------------------------------------------------
    # ÁREA INFERIOR
    # --------------------------------------------------

    def create_bottom_area(self):

        bottom = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
        )

        # LOG
        log_frame = Gtk.Frame(label="LOG DE EXECUÇÃO")

        scrolled = Gtk.ScrolledWindow()
        log_view = Gtk.TextView()
        scrolled.set_child(log_view)

        log_frame.set_child(scrolled)

        # CONTROLES
        control_frame = Gtk.Frame(
            label="CONTROLES DE EXECUÇÃO (PASSO A PASSO)"
        )

        control_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=15,
            margin_top=10,
            margin_bottom=10,
        )

        timeline = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=15
        )

        for i in range(1, 9):
            timeline.append(Gtk.Label(label=f"● {i}"))

        control_box.append(timeline)

        buttons = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10
        )

        buttons.append(Gtk.Button(label="▶ Próxima Etapa"))
        buttons.append(Gtk.Button(label="⏸ Pausar"))
        buttons.append(Gtk.Button(label="↺ Voltar Etapa"))

        control_box.append(buttons)

        control_frame.set_child(control_box)

        # ESTATÍSTICAS
        stats_frame = Gtk.Frame(label="ESTATÍSTICAS")

        stats_grid = Gtk.Grid(
            row_spacing=10,
            column_spacing=20,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10,
        )

        stats_grid.attach(Gtk.Label(label="Bits transmitidos:"), 0, 0, 1, 1)
        stats_grid.attach(Gtk.Label(label="512"), 1, 0, 1, 1)

        stats_grid.attach(Gtk.Label(label="Bits recebidos:"), 0, 1, 1, 1)
        stats_grid.attach(Gtk.Label(label="512"), 1, 1, 1, 1)

        stats_grid.attach(Gtk.Label(label="BER:"), 0, 2, 1, 1)
        stats_grid.attach(Gtk.Label(label="0.0000"), 1, 2, 1, 1)

        stats_frame.set_child(stats_grid)

        bottom.append(log_frame)
        bottom.append(control_frame)
        bottom.append(stats_frame)

        self.main_box.append(bottom)

    def startSimulation(self):
        print("opa")


class App(Gtk.Application):

    def __init__(self):
        super().__init__(
            application_id="com.simulador.digital"
        )

    def do_activate(self):
        win = MainWindow(self)
        win.present()


app = App()
app.run()