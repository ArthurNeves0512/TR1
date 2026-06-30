from codigo_fisica import camada_fisica
import numpy as np
from codigo_enlace import camada_enlace

class BitConverter:
    def __init__(self):
        pass

    def text_to_bits(self, text: str) -> str:
        return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

    def bits_to_text(self, bits: str) -> str:
        data = bytearray()
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) < 8:
                break
            data.append(int(byte, 2))
        return data.decode('utf-8')


class MaquinaEstados():
    def __init__(self, config, msg: str):
        self.config = config
        self.msg = msg

    def sending(self) -> np.ndarray:
        # Tamanho do quadro em BITS (se a config estiver em bytes, multiplique por 8)
        frame_size = int(self.config.get('frame_size', 8)) * 8 
        sinal_final = np.array([], dtype=np.float32)
        
        # Fragmentação: divide a mensagem em quadros menores
        for i in range(0, len(self.msg), frame_size):
            bloco_bits = self.msg[i:i + frame_size]
            
            # Cascata TX
            msg_com_edc = self.execute_error_detection(bloco_bits, True)
            msg_enquadrada = self.execute_framming(msg_com_edc, True)
            sinal_modulado = self.execute_modulation(msg_enquadrada, True)
            
            # Concatena os sinais analógicos gerados
            sinal_final = np.concatenate((sinal_final, sinal_modulado))
            
        return sinal_final

    def receving(self, array: np.ndarray) -> str:
        # Inverso da modulação (Transforma todo o array de tensão em bits)
        bits_totais = self.execute_modulation(array, False)
        
        # Neste ponto, precisamos desenquadrar. O ideal é que o próprio método 
        # de desenquadramento saiba encontrar as FLAGS para separar os frames,
        # mas como estamos processando sequencialmente:
        
        msg_desenq = self.execute_framming(bits_totais, False)
        
        # Se houve erro fatal no enquadramento e a string retornou vazia
        if not msg_desenq:
            return ""
            
        msg_sem_edc = self.execute_error_detection(msg_desenq, False)
        
        return BitConverter().bits_to_text(msg_sem_edc)

    def execute_framming(self, bits_str, isSending: bool) -> str:
        metodo_framming = self.config['framming_type']
        enlace = camada_enlace.CamadaEnlace()

        if metodo_framming == 'Contagem de Caracteres':
            if isSending:
                return enlace.enquadramento_contagem_caracteres(bits_str)
            dados, erro = enlace.desenquadramento_contagem_caracteres(bits_str)

        elif metodo_framming == 'Inserção Bytes':
            if isSending:
                return enlace.enquadramento_insercao_bytes(bits_str)
            dados, erro = enlace.desenquadramento_insercao_bytes(bits_str)

        elif metodo_framming == 'Inserção Bits':
            if isSending:
                return enlace.enquadramento_insercao_bits(bits_str)
            dados, erro = enlace.desenquadramento_insercao_bits(bits_str)
        else:
            return bits_str

        if erro:
            print(f"[Enlace RX] Erro de enquadramento: {erro}")
            return "" 

        return dados

    def execute_modulation(self, stream, isSending: bool):
        voltage_level = int(self.config['voltage_level'])
        modulation = self.config['modulation']
        
        # Agrupamentos para o roteamento (Preparando para a separação na UI)
        modulacoes_digitais = ['Nrz Polar', 'Bipolar', 'Manchester']
        modulacoes_analogicas = ['ASK', 'FSK', 'QPSK', '16-QAM']

        # Roteamento Digital (Banda Base)
        if modulation in modulacoes_digitais:
            if modulation == 'Nrz Polar':
                mod_class = camada_fisica.NrzPolar()
            elif modulation == 'Bipolar':
                mod_class = camada_fisica.Bipolar()
            elif modulation == 'Manchester':
                mod_class = camada_fisica.Manchester()
                
            if isSending:
                return mod_class.modulation(voltageLevel=voltage_level, bits_str=stream)
            return mod_class.desmodulation(voltageLevel=voltage_level, voltage_stream=stream)

        # Roteamento Analógico (Por Portadora)
        elif modulation in modulacoes_analogicas:
            if modulation == 'ASK':
                mod_class = camada_fisica.ASK()
            elif modulation == 'FSK':
                mod_class = camada_fisica.FSK()
            elif modulation == 'QPSK':
                mod_class = camada_fisica.QPSK()
            elif modulation == '16-QAM':
                mod_class = camada_fisica.QAM16()
                
            if isSending:
                return mod_class.modulation(amplitude=voltage_level, bits_str=stream)
            return mod_class.desmodulation(amplitude=voltage_level, sinal_modulado=stream)
            
        return stream

    def execute_error_detection(self, bits_str: str, isSending: bool) -> str:
        tipo = self.config.get('detection_type', '')
        enlace = camada_enlace.CamadaEnlace()

        if tipo == 'Paridade':
            if isSending:
                return enlace.enquadramento_paridade_par(bits_str)
            dados, erro = enlace.desenquadramento_paridade_par(bits_str)

        elif tipo == 'CheckSum':
            if isSending:
                return enlace.enquadramento_checksum(bits_str)
            dados, erro = enlace.desenquadramento_checksum(bits_str)

        elif tipo == 'CRC':
            if isSending:
                return enlace.enquadramento_crc(bits_str)
            dados, erro = enlace.desenquadramento_crc(bits_str)

        elif tipo == 'Hamming':
            if isSending:
                return enlace.enquadramento_hamming(bits_str)
            dados, erro = enlace.desenquadramento_hamming(bits_str)

        else:
            return bits_str 

        # Tratamento de Erro blindado contra falsos-positivos do Hamming
        if erro:
            if tipo == 'Hamming' and "corrigiu" in erro:
                print(f"[EDC RX] Aviso: {erro}")
                return dados # Hamming salvou o quadro, repassa os dados corrigidos
            
            print(f"[EDC RX] Falha crítica: {erro}")
            return ""
            
        return dados