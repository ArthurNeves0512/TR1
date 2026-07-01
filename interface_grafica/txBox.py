import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from sockets import client
from maquina_estados import maquina_estados


class TxBox:
    def __init__(self, cliente: client.Cliente):
        self.cliente = cliente
        self.config = {}

        self.entry_msg = Gtk.Entry(text="b")
        self.tv_bits_puros, self.scroll_puros = self.create_readonly_textview()
        self.tv_bits_enquadrados, self.scroll_enquadrados = self.create_readonly_textview()

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

    def setupTx(self) -> Gtk.Frame:
        # Mantém os mesmos campos da interface original.
        frame = Gtk.Frame(label="Transmissor (Tx)")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=10)

        vbox.pack_start(Gtk.Label(label="1. Entrada de Texto (Digite aqui):", xalign=0), False, False, 0)
        vbox.pack_start(self.entry_msg, False, False, 0)

        vbox.pack_start(Gtk.Label(label="2. Visualização de Bits Puros:", xalign=0), False, False, 0)
        vbox.pack_start(self.scroll_puros, True, True, 0)

        vbox.pack_start(Gtk.Label(label="3. Visualização de Bits (Enquadrados + EDC):", xalign=0), False, False, 0)
        vbox.pack_start(self.scroll_enquadrados, True, True, 0)

        frame.add(vbox)
        return frame

    def on_send_clicked(self, sender_widget=None):
        mensagem = self.entry_msg.get_text()

        try:
            state_machine = maquina_estados.MaquinaEstados(self.config, mensagem)
            array_sinal = state_machine.sending()

            self.set_text_safe(self.tv_bits_puros, state_machine.bits_puros)
            # Os quadros continuam no mesmo campo que já existia.
            self.set_text_safe(self.tv_bits_enquadrados, state_machine.msg_enquadrada)

            print("TX enviando sinal para o socket...")
            sucesso, erro = self.cliente.send_message(array=array_sinal)
            if not sucesso:
                self.set_text_safe(self.tv_bits_enquadrados, f"Erro no socket: {erro}")

        except Exception as erro:
            self.set_text_safe(self.tv_bits_enquadrados, f"Erro: {erro}")

    def update_configuration(self, config):
        self.config = config
