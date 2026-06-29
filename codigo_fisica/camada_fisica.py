import numpy as np
import matplotlib.pyplot as plt

# Modulações digitais

class NrzPolar:
    def modulation(self, voltageLevel: float, bits_str: str) -> np.ndarray:
        voltage_stream = np.zeros(shape=(len(bits_str)),dtype=np.float32)
        for index, bit in enumerate(bits_str):
            voltage_stream[index] = voltageLevel if bit == '1' else -voltageLevel
        return voltage_stream

    def demodulation(self, voltageLevel: float, voltage_stream: np.ndarray) -> str:
        bits = ''
        voltage_stream = np.asarray(voltage_stream, dtype=np.float32)
        for voltage in voltage_stream:
            print(type(voltage), voltage)
            bits += '1' if voltage > 0 else '0'
        return bits


class Manchester:
    def modulation(self, voltageLevel: float, bits_str: str) -> np.ndarray:
        voltage_stream = np.zeros(len(bits_str) * 2,dtype=np.float32)

        for i, bit in enumerate(bits_str):
            idx = i * 2
            if bit == '1':
                voltage_stream[idx] = voltageLevel
                voltage_stream[idx + 1] = -voltageLevel
            else:
                voltage_stream[idx] = -voltageLevel
                voltage_stream[idx + 1] = voltageLevel

        return voltage_stream

    def demodulation(self, voltageLevel: float, voltage_stream: np.ndarray) -> str:
        bits_recuperados = ""
        for i in range(0, len(voltage_stream), 2):
            primeira_metade = voltage_stream[i]
            bits_recuperados += '1' if primeira_metade > 0 else '0'
        return bits_recuperados

class Bipolar:
    def modulation(self, voltageLevel: float, bits_str: str) -> np.ndarray:
        voltage_stream = np.zeros(len(bits_str),dtype=np.float32)
        inversor = 1

        for i, bit in enumerate(bits_str):
            if bit == '1':
                voltage_stream[i] = voltageLevel * inversor
                inversor *= -1
            else:
                voltage_stream[i] = 0

        return voltage_stream

    def demodulation(self, voltageLevel: float, voltage_stream: np.ndarray) -> str:
        bits_recuperados = ""
        limiar = voltageLevel / 2
        for tensao in voltage_stream:
            bits_recuperados += '1' if abs(tensao) > limiar else '0'
        return bits_recuperados


# Modulações por portadora

class ASK:
    def __init__(self, amostras_por_bit=200, fc=5):
        self.amostras_por_bit = amostras_por_bit
        self.fc = fc

    def modulation(self, amplitude: float, bits_str: str) -> np.ndarray:
        t = np.linspace(0, 1, self.amostras_por_bit, endpoint=False,dtype=np.float32)
        onda_portadora = amplitude * np.sin(2 * np.pi * self.fc *t)
        onda_morta = np.zeros(self.amostras_por_bit)

        sinal_transmitido = np.zeros(len(bits_str) * self.amostras_por_bit,dtype=np.float32)
        
        for i, bit in enumerate(bits_str):
            idx_inicio = i * self.amostras_por_bit
            idx_fim = idx_inicio + self.amostras_por_bit
            
            sinal_transmitido[idx_inicio:idx_fim] = onda_portadora if float(bit) == 1 else onda_morta
        return sinal_transmitido

    def demodulation(self, amplitude: float, sinal_modulado: np.ndarray) -> str:
        bits_recuperados:str = ""
        t = np.linspace(0, 1, self.amostras_por_bit, endpoint=False,dtype=np.float32)
        onda_referencia = np.sin(2 * np.pi * self.fc * t)
        energia_bit_um = amplitude * np.sum(onda_referencia ** 2)
        limiar = energia_bit_um / 2

        for i in range(0, len(sinal_modulado), self.amostras_por_bit):
            bloco_sinal = sinal_modulado[i:i + self.amostras_por_bit]
            correlacao = np.sum(bloco_sinal * onda_referencia)
            if(correlacao > limiar):
                bits_recuperados = bits_recuperados+"1"
            else:
                bits_recuperados = bits_recuperados+"0"

        return bits_recuperados

class FSK:
    def __init__(self, amostras_por_bit=200, fc0=2, fc1=5):
        self.amostras_por_bit = amostras_por_bit
        self.fc0 = fc0
        self.fc1 = fc1
        self.t = np.linspace(0, 1, amostras_por_bit, endpoint=False, dtype=np.float32)

    def modulation(self, amplitude: float, bits_str: str) -> np.ndarray:

        onda_0 = amplitude * np.sin(2 * np.pi * self.fc0 * self.t)
        onda_1 = amplitude * np.sin(2 * np.pi * self.fc1 * self.t)

        sinal = np.zeros(len(bits_str) * self.amostras_por_bit, dtype=np.float32)

        for i, bit in enumerate(bits_str):
            idx = i * self.amostras_por_bit

            if bit == '1':
                sinal[idx:idx + self.amostras_por_bit] = onda_1
            else:
                sinal[idx:idx + self.amostras_por_bit] = onda_0

        return sinal
    

    
    def demodulation(self, amplitude: float, sinal_modulado: np.ndarray) -> str:

        bits = ""

        ref0 = amplitude*np.sin(2 * np.pi * self.fc0 * self.t)
        ref1 = amplitude*np.sin(2 * np.pi * self.fc1 * self.t)

        for i in range(0, len(sinal_modulado), self.amostras_por_bit):

            bloco = sinal_modulado[i:i + self.amostras_por_bit]

            corr0 = np.dot(bloco, ref0) 
            corr1 = np.dot(bloco, ref1) 

            if corr1 > corr0:
                bits += "1"
            else:
                bits += "0"

        return bits

class QPSK:
    def __init__(self, amostras_por_simbolo=200, fc=2):
        self.amostras_por_simbolo = amostras_por_simbolo
        self.fc = fc
        
        self.constelacao={
            '00': {'I':-1,'Q':-1},
            '01': {'I':-1,'Q':1},
            '11': {'I':1,'Q':1},
            '10': {'I':1,'Q':-1},
        }
        self.constelacao_rx = {
            (-1, -1): '00',
            (-1,  1): '01',
            ( 1,  1): '11',
            ( 1, -1): '10',
        }

    def modulation(self, amplitude: float, bits_str: str) -> np.ndarray:
        if len(bits_str) % 2 != 0:
            bits_str += '0'

        t = np.linspace(0, 1, self.amostras_por_simbolo, endpoint=False,dtype=np.float32)
        num_simbolos = len(bits_str) // 2
        sinal_transmitido = np.zeros(num_simbolos * self.amostras_por_simbolo,dtype=np.float32)
        cos = np.cos(2 * np.pi * self.fc * t)
        sen = - np.sin(2 * np.pi * self.fc * t)
        for contador_de_amostras, iterador_bits in enumerate(range(0, len(bits_str), 2)):
            i_bit = bits_str[iterador_bits]
            q_bit = bits_str[iterador_bits+1]
            I_t= self.constelacao[i_bit+q_bit].get('I')*cos*amplitude
            Q_t = self.constelacao[i_bit+q_bit].get('Q')*sen*amplitude
            sinal_final = I_t + Q_t

            inicio = contador_de_amostras * self.amostras_por_simbolo
            fim = inicio + self.amostras_por_simbolo
            sinal_transmitido[inicio:fim] = sinal_final
        return sinal_transmitido

    def demodulation(self, sinal_recebido: np.ndarray) -> str:

        t = np.linspace(
            0,
            1,
            self.amostras_por_simbolo,
            endpoint=False,
            dtype=np.float32
        )

        cos = np.cos(2 * np.pi * self.fc * t)
        sen = -np.sin(2 * np.pi * self.fc * t)

        bits = ""

        num_simbolos = len(sinal_recebido) // self.amostras_por_simbolo

        for simbolo in range(num_simbolos):

            inicio = simbolo * self.amostras_por_simbolo
            fim = inicio + self.amostras_por_simbolo

            sinal = sinal_recebido[inicio:fim]

            I = np.dot(sinal, cos)
            Q = np.dot(sinal, sen)
            
            I = 1 if I >= 0 else -1
            Q = 1 if Q >= 0 else -1

            bits += self.constelacao_rx[(I, Q)]

        return bits

class QAM16:
    def __init__(self, amostras_por_simbolo=200, fc=2):
        self.amostras_por_simbolo = amostras_por_simbolo
        self.fc = fc
        self.niveis = {'00': -3, '01': -1, '10': 1, '11': 3}
        self.niveis_reverso = {-3: '00', -1: '01', 1: '10', 3: '11'}

    def modulation(self, amplitude_base: float, bits_str: str) -> np.ndarray:
        while len(bits_str) % 4 != 0:
            bits_str += '0'

        t = np.linspace(0, 1, self.amostras_por_simbolo, endpoint=False)
        num_simbolos = len(bits_str) // 4
        sinal_transmitido = np.zeros(num_simbolos * self.amostras_por_simbolo)

        for j, i in enumerate(range(0, len(bits_str), 4)):
            bits_i = bits_str[i:i + 2]
            bits_q = bits_str[i + 2:i + 4]

            amp_i = self.niveis[bits_i] * amplitude_base
            amp_q = self.niveis[bits_q] * amplitude_base

            onda = (amp_i * np.sin(2 * np.pi * self.fc * t)) + (amp_q * np.cos(2 * np.pi * self.fc * t))
            
            idx_inicio = j * self.amostras_por_simbolo
            idx_fim = idx_inicio + self.amostras_por_simbolo
            sinal_transmitido[idx_inicio:idx_fim] = onda

        return sinal_transmitido

    def demodulation(self, amplitude_base: float, sinal_modulado: np.ndarray) -> str:
        bits_recuperados = ""
        t = np.linspace(0, 1, self.amostras_por_simbolo, endpoint=False)
        niveis_possiveis = np.array([-3, -1, 1, 3]) * amplitude_base

        for i in range(0, len(sinal_modulado), self.amostras_por_simbolo):
            bloco_sinal = sinal_modulado[i:i + self.amostras_por_simbolo]

            valor_i = np.mean(bloco_sinal * np.sin(2 * np.pi * self.fc * t)) * 2
            valor_q = np.mean(bloco_sinal * np.cos(2 * np.pi * self.fc * t)) * 2

            nivel_i_estimado = niveis_possiveis[np.argmin(np.abs(niveis_possiveis - valor_i))]
            nivel_q_estimado = niveis_possiveis[np.argmin(np.abs(niveis_possiveis - valor_q))]

            chave_i = int(round(nivel_i_estimado / amplitude_base))
            chave_q = int(round(nivel_q_estimado / amplitude_base))

            bits_recuperados += self.niveis_reverso[chave_i] + self.niveis_reverso[chave_q]

        return bits_recuperados


# Ruido Gaussiano

class Canal:
    def adicionar_ruido(self, sinal: np.ndarray, x: float = 0.0, sigma: float = 0.5) -> np.ndarray:
        ruido = np.random.normal(loc=x, scale=sigma, size=len(sinal))
        return sinal + ruido

    """"# Área de testes local lembrar de apagar depois."""
if __name__ == '__main__':
    a = QPSK().modulation(1,'111010110000')

    print(QPSK().demodulation(a))