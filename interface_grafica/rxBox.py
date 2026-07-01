import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from maquina_estados import maquina_estados


class RxBox:
    def __init__(self, servidor):
        self.config = {}
        self.servidor = servidor
        self.retransmit_callback = None

        self.tv_bits_desmod, self.scroll_desmod = self.create_readonly_textview()
        self.tv_bits_desenq, self.scroll_desenq = self.create_readonly_textview()
        self.tv_texto_final, self.scroll_final = self.create_readonly_textview()

        self.btn_retransmitir = Gtk.Button(label="Erro Detectado! Solicitar Retransmissão")
        self.btn_retransmitir.connect("clicked", self.solicitar_retransmissao)
        self.btn_retransmitir.set_no_show_all(True)

        self.servidor.set_callback(self.on_data_received)

    def create_readonly_textview(self):
        tv = Gtk.TextView()
        tv.set_editable(False)
        tv.set_cursor_visible(False)
        tv.set_wrap_mode(Gtk.WrapMode.CHAR)
        tv.override_background_color(
            Gtk.StateFlags.NORMAL,
            gi.repository.Gdk.RGBA(0.95, 0.95, 0.95, 1),
        )

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(50)
        scroll.add(tv)
        return tv, scroll

    def set_text_safe(self, textview, text):
        textview.get_buffer().set_text(str(text))

    def set_retransmit_callback(self, callback):
        self.retransmit_callback = callback

    def setupRx(self) -> Gtk.Frame:
        # Mantém exatamente os três campos do receptor original.
        frame = Gtk.Frame(label="Receptor (Rx)")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=10)

        vbox.pack_start(Gtk.Label(label="1. Visualização de Bits (Desmodulados):", xalign=0), False, False, 0)
        vbox.pack_start(self.scroll_desmod, True, True, 0)

        vbox.pack_start(Gtk.Label(label="2. Visualização de Bits (Desenquadrados + EDC):", xalign=0), False, False, 0)
        vbox.pack_start(self.scroll_desenq, True, True, 0)

        vbox.pack_start(Gtk.Label(label="3. Saída de Texto Final:", xalign=0), False, False, 0)
        vbox.pack_start(self.scroll_final, True, True, 0)

        vbox.pack_start(self.btn_retransmitir, False, False, 0)

        frame.add(vbox)
        return frame

    def solicitar_retransmissao(self, widget):
        self.btn_retransmitir.hide()
        self.set_text_safe(self.tv_texto_final, "Aguardando nova transmissão...")
        if self.retransmit_callback:
            self.retransmit_callback()

    def update_ui(self, sucesso, msg_final, aviso_edc="", erro="", bits_desmod="", bits_desenq=""):
        self.set_text_safe(self.tv_bits_desmod, bits_desmod)
        self.set_text_safe(self.tv_bits_desenq, bits_desenq)

        if sucesso:
            texto_saida = str(msg_final)
            if aviso_edc:
                texto_saida += f"\n\n{aviso_edc}"
            self.set_text_safe(self.tv_texto_final, texto_saida)
            self.btn_retransmitir.hide()
        else:
            self.set_text_safe(self.tv_texto_final, f"Erro de Transmissão: {erro}")
            self.btn_retransmitir.show()

        return False

    def on_data_received(self, data):
        machine = maquina_estados.MaquinaEstados(self.config, msg="")
        mensagem_final = machine.receving(data)

        GLib.idle_add(
            self.update_ui,
            machine.sucesso,
            mensagem_final if machine.sucesso else "",
            machine.aviso_edc or "",
            machine.erro_transmissao or "",
            getattr(machine, "msg_desmodularizada", ""),
            getattr(machine, "msg_desenquadrada", ""),
        )

    def update_configuration(self, config):
        self.config = config
