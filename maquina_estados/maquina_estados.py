from codigo_fisica import camada_fisica
from codigo_enlace import camada_enlace
import matplotlib.pyplot as plt
import numpy as np


def plot_sinal_analogico(
    sinal_original,
    sinal_ruidoso=None,
    amostras_por_bit=200,
    titulo="Sinal Modulado",
):
    sinal_original = np.asarray(sinal_original)
    plt.figure(figsize=(12, 3))

    if sinal_ruidoso is not None:
        sinal_ruidoso = np.asarray(sinal_ruidoso)
        plt.plot(sinal_original, color="blue", linewidth=3, label="Sinal Original", alpha=0.4)
        plt.plot(sinal_ruidoso, color="red", linewidth=1.2, label="Sinal com Ruído", alpha=0.9)
        plt.legend(loc="upper right")
    else:
        plt.plot(sinal_original, color="blue", linewidth=1.5)

    for i in range(0, len(sinal_original), amostras_por_bit):
        plt.axvline(i, color="gray", linestyle="--", alpha=0.3)

    plt.title(titulo)
    plt.xlabel("Amostras")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()


def plot_sinal_digital(
    sinal_original,
    sinal_ruidoso=None,
    amostras_por_bit=None,
    titulo="Sinal Digital",
):
    sinal_original = np.asarray(sinal_original)
    if len(sinal_original) == 0:
        return

    x = np.arange(len(sinal_original) + 1)
    y_orig = np.append(sinal_original, sinal_original[-1])
    plt.figure(figsize=(12, 3))

    if sinal_ruidoso is not None:
        sinal_ruidoso = np.asarray(sinal_ruidoso)
        y_ruido = np.append(sinal_ruidoso, sinal_ruidoso[-1])
        plt.step(x, y_orig, where="post", color="blue", linewidth=3, label="Sinal Original", alpha=0.4)
        plt.step(x, y_ruido, where="post", color="red", linewidth=1.2, label="Sinal com Ruído", alpha=0.9)
        plt.legend(loc="upper right")
    else:
        plt.step(x, y_orig, where="post", color="blue", linewidth=1.5)

    if amostras_por_bit is not None:
        for i in range(0, len(sinal_original), amostras_por_bit):
            plt.axvline(i, color="gray", linestyle="--", alpha=0.4)

    plt.title(titulo)
    plt.xlabel("Amostras")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()


class BitConverter:
    def text_to_bits(self, text: str) -> str:
        return "".join(format(byte, "08b") for byte in text.encode("utf-8"))

    def bits_to_text(self, bits: str) -> str:
        if len(bits) % 8 != 0:
            raise ValueError("Os bits recebidos não formam bytes completos.")

        dados = bytearray(
            int(bits[i:i + 8], 2)
            for i in range(0, len(bits), 8)
        )
        return dados.decode("utf-8", errors="strict")


class MaquinaEstados:
    def __init__(self, config, msg: str):
        self.config = config
        self.msg = msg
        self.enlace = camada_enlace.CamadaEnlace(self.config)

        self.sucesso = False
        self.erro_transmissao = None
        self.aviso_edc = None
        self.mensagem_final = ""
        self.quadros_tx = []
        self.quadros_rx = []

    def _falhar(self, mensagem):
        self.sucesso = False
        self.erro_transmissao = mensagem
        self.mensagem_final = ""
        return f"Erro de Transmissão: {mensagem}"

    def execute_error_control(self, bits_str: str, isSending: bool):
        tipo_erro = self.config.get("error_control", "Nenhum")

        if isSending:
            if tipo_erro == "Paridade Par":
                return self.enlace.enquadramento_paridade_par(bits_str)
            if tipo_erro == "Checksum":
                return self.enlace.enquadramento_checksum(bits_str)
            if tipo_erro == "CRC-32":
                return self.enlace.enquadramento_crc(bits_str)
            if tipo_erro == "Hamming":
                return self.enlace.enquadramento_hamming(bits_str)
            if tipo_erro == "Nenhum":
                return bits_str
        else:
            if tipo_erro == "Paridade Par":
                return self.enlace.desenquadramento_paridade_par(bits_str)
            if tipo_erro == "Checksum":
                return self.enlace.desenquadramento_checksum(bits_str)
            if tipo_erro == "CRC-32":
                return self.enlace.desenquadramento_crc(bits_str)
            if tipo_erro == "Hamming":
                return self.enlace.desenquadramento_hamming(bits_str)
            if tipo_erro == "Nenhum":
                return bits_str, None

        raise ValueError(f"Controle de erro desconhecido: {tipo_erro}")

    def _adicionar_padding_enlace(self, bits_com_edc):
        metodo = self.config.get("framming_type")
        if metodo in ("Contagem de Caracteres", "Inserção Bytes"):
            padding = (-len(bits_com_edc)) % 8
        else:
            padding = 0

        self.config["padding_enlace"] = padding
        self.config["tamanho_real_edc"] = len(bits_com_edc)
        return bits_com_edc + ("0" * padding)

    def _adicionar_padding_modulacao(self, bits_enquadrados):
        modulacao = self.config.get("modulation")
        bits_por_simbolo = 1
        if modulacao == "QPSK":
            bits_por_simbolo = 2
        elif modulacao == "16-QAM":
            bits_por_simbolo = 4

        padding = (-len(bits_enquadrados)) % bits_por_simbolo
        self.config["padding_modulacao"] = padding
        return bits_enquadrados + ("0" * padding)

    def sending(self):
        media_erro = float(self.config.get("media_erro", 0.0))
        sigma_erro = float(self.config.get("sigma_erro", 0.0))

        if media_erro < 0 or sigma_erro < 0:
            raise ValueError("Os valores de ruído não podem ser negativos.")
        if self.msg == "":
            raise ValueError("Digite uma mensagem antes de iniciar a transmissão.")

        # Aplicação: texto para bits.
        self.bits_puros = BitConverter().text_to_bits(self.msg)

        # Enlace: adiciona EDC e depois faz o enquadramento.
        self.bits_com_edc = self.execute_error_control(self.bits_puros, True)
        bits_para_enquadrar = self._adicionar_padding_enlace(self.bits_com_edc)
        self.msg_enquadrada = self.execute_framming(bits_para_enquadrar, True)
        self.quadros_tx = list(self.enlace.ultimos_quadros)
        self.msg_enquadrada_visual = " | ".join(self.quadros_tx)

        # Evita que QPSK e 16-QAM adicionem bits que o receptor desconhece.
        self.msg_para_modular = self._adicionar_padding_modulacao(self.msg_enquadrada)
        self.msg_modulation = np.asarray(
            self.execute_modulation(self.msg_para_modular, True),
            dtype=np.float32,
        )

        plt.close("all")

        if sigma_erro != 0 or media_erro != 0:
            ruido = np.random.normal(
                media_erro,
                sigma_erro,
                len(self.msg_modulation),
            ).astype(np.float32)
            msg_final = (self.msg_modulation + ruido).astype(np.float32)

            if self.config["modulation"] in ["ASK", "FSK", "QPSK", "16-QAM"]:
                plot_sinal_analogico(
                    self.msg_modulation,
                    sinal_ruidoso=msg_final,
                    titulo=f"Sinal {self.config['modulation']} (Com Ruído)",
                )
            else:
                plot_sinal_digital(
                    self.msg_modulation,
                    sinal_ruidoso=msg_final,
                    titulo=f"Sinal {self.config['modulation']} (Com Ruído)",
                )
        else:
            msg_final = self.msg_modulation.astype(np.float32)
            if self.config["modulation"] in ["ASK", "FSK", "QPSK", "16-QAM"]:
                plot_sinal_analogico(
                    msg_final,
                    titulo=f"Sinal {self.config['modulation']} Limpo",
                )
            else:
                plot_sinal_digital(
                    msg_final,
                    titulo=f"Sinal {self.config['modulation']} Limpo",
                )

        plt.show(block=False)
        return msg_final

    def receving(self, array: np.ndarray):
        try:
            self.msg_desmodularizada = self.execute_modulation(array, False)

            padding_modulacao = int(self.config.get("padding_modulacao", 0))
            if padding_modulacao < 0 or padding_modulacao > len(self.msg_desmodularizada):
                return self._falhar("Padding da modulação inválido.")

            if padding_modulacao:
                bits_para_desenquadrar = self.msg_desmodularizada[:-padding_modulacao]
            else:
                bits_para_desenquadrar = self.msg_desmodularizada

            self.bits_para_desenquadrar = bits_para_desenquadrar
            self.msg_desenquadrada, erro_framing = self.execute_framming(
                bits_para_desenquadrar,
                False,
            )
            self.quadros_rx = list(self.enlace.ultimos_quadros)
            self.quadros_rx_visual = " | ".join(self.quadros_rx)

            if erro_framing:
                return self._falhar(erro_framing)

            padding_enlace = int(self.config.get("padding_enlace", 0))
            if padding_enlace < 0 or padding_enlace > len(self.msg_desenquadrada):
                return self._falhar("Padding da camada de enlace inválido.")

            if padding_enlace:
                bits_limpos_para_edc = self.msg_desenquadrada[:-padding_enlace]
            else:
                bits_limpos_para_edc = self.msg_desenquadrada

            tamanho_real = int(self.config.get("tamanho_real_edc", len(bits_limpos_para_edc)))
            if len(bits_limpos_para_edc) != tamanho_real:
                return self._falhar("O tamanho recuperado não corresponde ao tamanho do EDC enviado.")

            self.msg_verificada, self.aviso_edc = self.execute_error_control(
                bits_limpos_para_edc,
                False,
            )
            if self.msg_verificada is None:
                return self._falhar(self.aviso_edc or "Falha no controle de erros.")

            try:
                self.mensagem_final = BitConverter().bits_to_text(self.msg_verificada)
            except (ValueError, UnicodeDecodeError):
                return self._falhar("Os bits recuperados não formam uma mensagem UTF-8 válida.")

            self.sucesso = True
            self.erro_transmissao = None
            return self.mensagem_final

        except (ValueError, TypeError, KeyError) as erro:
            return self._falhar(str(erro))

    def execute_framming(self, bits_str, isSending: bool):
        metodo = self.config.get("framming_type")

        if metodo == "Contagem de Caracteres":
            if isSending:
                return self.enlace.enquadramento_contagem_caracteres(bits_str)
            return self.enlace.desenquadramento_contagem_caracteres(bits_str)

        if metodo == "Inserção Bytes":
            if isSending:
                return self.enlace.enquadramento_insercao_bytes(bits_str)
            return self.enlace.desenquadramento_insercao_bytes(bits_str)

        if metodo == "Inserção Bits":
            if isSending:
                return self.enlace.enquadramento_insercao_bits(bits_str)
            return self.enlace.desenquadramento_insercao_bits(bits_str)

        raise ValueError(f"Enquadramento desconhecido: {metodo}")

    def execute_modulation(self, bits_str, isSending: bool) -> np.ndarray:
        voltage_level = int(self.config["voltage_level"])
        modulation = self.config["modulation"]

        if modulation == "Nrz Polar":
            if isSending:
                return camada_fisica.NrzPolar().modulation(
                    voltageLevel=voltage_level,
                    bits_str=bits_str,
                )
            return camada_fisica.NrzPolar().demodulation(
                voltageLevel=voltage_level,
                voltage_stream=bits_str,
            )

        if modulation == "Bipolar":
            if isSending:
                return camada_fisica.Bipolar().modulation(
                    voltageLevel=voltage_level,
                    bits_str=bits_str,
                )
            return camada_fisica.Bipolar().demodulation(
                voltageLevel=voltage_level,
                voltage_stream=bits_str,
            )

        if modulation == "Manchester":
            if isSending:
                return camada_fisica.Manchester().modulation(
                    voltageLevel=voltage_level,
                    bits_str=bits_str,
                )
            return camada_fisica.Manchester().demodulation(
                voltageLevel=voltage_level,
                voltage_stream=bits_str,
            )

        if modulation == "ASK":
            if isSending:
                return camada_fisica.ASK(amostras_por_bit=200).modulation(
                    self.config["voltage_level"],
                    bits_str=bits_str,
                )
            return camada_fisica.ASK().demodulation(
                amplitude=self.config["voltage_level"],
                sinal_modulado=bits_str,
            )

        if modulation == "FSK":
            if isSending:
                return camada_fisica.FSK().modulation(
                    self.config["voltage_level"],
                    bits_str=bits_str,
                )
            return camada_fisica.FSK().demodulation(
                amplitude=self.config["voltage_level"],
                sinal_modulado=bits_str,
            )

        if modulation == "QPSK":
            if isSending:
                return camada_fisica.QPSK().modulation(
                    self.config["voltage_level"],
                    bits_str=bits_str,
                )
            return camada_fisica.QPSK().demodulation(bits_str)

        if modulation == "16-QAM":
            if isSending:
                return camada_fisica.QAM16().modulation(
                    self.config["voltage_level"],
                    bits_str=bits_str,
                )
            return camada_fisica.QAM16().demodulation(
                self.config["voltage_level"],
                bits_str=bits_str,
            )

        raise ValueError(f"Modulação desconhecida: {modulation}")
