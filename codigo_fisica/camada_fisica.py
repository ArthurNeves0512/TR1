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
            bits += '1' if voltage > 0 else '0'
        return bits


class Manchester:
    def modulation(self, voltageLevel: float, bits_str: str) -> np.ndarray:
        voltage_stream = np.zeros(len(bits_str) * 2,dtype=np.float32)

        for i, bit in enumerate(bits_str):
            idx = i * 2
            if bit == '1':
                # o sinal de clock esta implicito bem aqui, ja que cada bit dura um ciclo.
                voltage_stream[idx] = voltageLevel
                voltage_stream[idx + 1] = -voltageLevel
            else:
                # o sinal de clock esta implicito bem aqui, ja que cada bit dura um ciclo.
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
        #cria 200 valores de 0 até 1 
        t = np.linspace(0, 1, self.amostras_por_bit, endpoint=False,dtype=np.float32)

        onda_portadora = amplitude * np.sin(2 * np.pi * self.fc *t)
        onda_morta = np.zeros(self.amostras_por_bit,dtype=np.float32)

        sinal_transmitido = np.zeros(len(bits_str) * self.amostras_por_bit,dtype=np.float32)
        
        for i, bit in enumerate(bits_str):
            idx_inicio = i * self.amostras_por_bit
            idx_fim = idx_inicio + self.amostras_por_bit
            
            sinal_transmitido[idx_inicio:idx_fim] = onda_portadora if float(bit) == 1 else onda_morta
        return sinal_transmitido

    def demodulation(self, amplitude: float, sinal_modulado: np.ndarray) -> str:
        bits_recuperados = ""
        limiar = amplitude / 2  # Se o pico passar da metade da amplitude, é 1.

        for i in range(0, len(sinal_modulado), self.amostras_por_bit):
            bloco_sinal = sinal_modulado[i:i + self.amostras_por_bit]
            pico_maximo = np.max(np.abs(bloco_sinal))
            if pico_maximo > limiar:
                bits_recuperados += "1"
            else:
                bits_recuperados += "0"

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
        
        ref0 = amplitude * np.sin(2 * np.pi * self.fc0 * self.t)
        ref1 = amplitude * np.sin(2 * np.pi * self.fc1 * self.t)
        #aqui a gente basicamente quer saber a média da diferenca entre cada amostra
        #e para frequencias maiores, temos uma diferenca maior entre cada ponto
        derivada_0 = np.mean(np.abs(np.diff(ref0)))
        derivada_1 = np.mean(np.abs(np.diff(ref1)))
        limiar = (derivada_0 + derivada_1) / 2

        for i in range(0, len(sinal_modulado), self.amostras_por_bit):
            bloco = sinal_modulado[i:i + self.amostras_por_bit]
            derivada_bloco = np.mean(np.abs(np.diff(bloco)))

            if derivada_bloco > limiar:
                bits += "1"
            else:
                bits += "0"

        return bits

class QPSK:
    def __init__(self, amostras_por_simbolo=200, fc=2):
        self.amostras_por_simbolo = amostras_por_simbolo
        self.fc = fc
        
        self.constelacao={
            '00': {'I':1,'Q':1}, #π/4
            '01': {'I':-1,'Q':1},#3π/4
            '11': {'I':-1,'Q':-1},#5π/4
            '10': {'I':1,'Q':-1},#7π/4
        }
        self.constelacao_rx = {
            (1, 1): '00',
            (-1,  1): '01',
            ( -1,  -1): '11',
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
            I_t = self.constelacao[i_bit+q_bit].get('I')*cos*amplitude
            Q_t = self.constelacao[i_bit+q_bit].get('Q')*sen*amplitude
            sinal_final = I_t + Q_t

            inicio = contador_de_amostras * self.amostras_por_simbolo
            fim = inicio + self.amostras_por_simbolo
            sinal_transmitido[inicio:fim] = sinal_final
        return sinal_transmitido

    def demodulation(self, sinal_recebido: np.ndarray) -> str:
        t = np.linspace(0, 1, self.amostras_por_simbolo, endpoint=False, dtype=np.float32)
        cos = np.cos(2 * np.pi * self.fc * t)
        sen = -np.sin(2 * np.pi * self.fc * t)

        bits = ""
        num_simbolos = len(sinal_recebido) // self.amostras_por_simbolo

        for simbolo in range(num_simbolos):
            inicio = simbolo * self.amostras_por_simbolo
            fim = inicio + self.amostras_por_simbolo
            bloco = sinal_recebido[inicio:fim]

            correlacao_I = np.dot(bloco,cos)
            correlacao_Q = np.dot(bloco,sen)
            
            I = 1 if correlacao_I >= 0 else -1
            Q = 1 if correlacao_Q >= 0 else -1

            bits += self.constelacao_rx[(I, Q)]

        return bits

class QAM16:
    def __init__(self, amostras_por_simbolo=200, fc=2):
        self.amostras_por_simbolo = amostras_por_simbolo
        self.fc = fc
        sqrt_two = np.sqrt(2)
        self.constelacao = {
            '0000': {'I':-1/(3*sqrt_two),'Q':-1/(3*sqrt_two)},
            '0001': {'I':-1/(3*sqrt_two),'Q':-1/sqrt_two},
            '0010': {'I':-1/sqrt_two,'Q':-1/(3*sqrt_two)},
            '0011': {'I':-1/sqrt_two,'Q':-1/sqrt_two},
            '0100': {'I':-1/(3*sqrt_two),'Q': 1/(3*sqrt_two)},
            '0101': {'I':-1/(3*sqrt_two),'Q': 1/sqrt_two},
            '0110': {'I':-1/sqrt_two,'Q': 1/(3*sqrt_two)},
            '0111': {'I':-1/sqrt_two,'Q': 1/sqrt_two},
            '1000': {'I': 1/(3*sqrt_two),'Q':-1/(3*sqrt_two)},
            '1001': {'I': 1/(3*sqrt_two),'Q':-1/sqrt_two},
            '1010': {'I': 1/sqrt_two,'Q':-1/(3*sqrt_two)},
            '1011': {'I': 1/sqrt_two,'Q':-1/sqrt_two},
            '1100': {'I': 1/(3*sqrt_two),'Q': 1/(3*sqrt_two)},
            '1101': {'I': 1/(3*sqrt_two),'Q': 1/sqrt_two},
            '1110': {'I': 1/sqrt_two,'Q': 1/(3*sqrt_two)},
            '1111': {'I': 1/sqrt_two,'Q': 1/sqrt_two},
        }

    def modulation(self, amplitude, bits_str):
        while len(bits_str) % 4 != 0:
            bits_str += "0"

        t = np.linspace(0, 1, self.amostras_por_simbolo, endpoint=False, dtype=np.float32)
        cos = np.cos(2*np.pi*self.fc*t)
        sen = -np.sin(2*np.pi*self.fc*t)
        num_simbolos = len(bits_str)//4
        sinal = np.zeros(num_simbolos*self.amostras_por_simbolo, dtype=np.float32)

        for simbolo, i in enumerate(range(0, len(bits_str), 4)):
            nibble = bits_str[i:i+4]
            I = amplitude*self.constelacao[nibble]["I"]
            Q = amplitude*self.constelacao[nibble]["Q"]
            onda = I*cos + Q*sen
            inicio = simbolo*self.amostras_por_simbolo
            fim = inicio+self.amostras_por_simbolo
            sinal[inicio:fim] = onda

        return sinal

    def demodulation(self, amplitude, bits_str):

        #basicamente o que estamos fazendo é veja se nos index de picos do sen e cos se são parecidos com o do seu dado
        t = np.linspace(0, 1, self.amostras_por_simbolo, endpoint=False, dtype=np.float32)
        cos = np.cos(2*np.pi*self.fc*t)
        sen = -np.sin(2*np.pi*self.fc*t)
        #pegamos o index do valor de pico, aqui para o cos por exemplo o index é sempre 0 
        idx_I_pico = np.argmax(cos)
        idx_Q_pico = np.argmax(sen)

        bits = ""
        num_simbolos = len(bits_str)//self.amostras_por_simbolo

        for simbolo in range(num_simbolos):
            inicio = simbolo*self.amostras_por_simbolo
            fim = inicio+self.amostras_por_simbolo
            bloco = bits_str[inicio:fim]

            I_rx = bloco[idx_I_pico] / amplitude
            Q_rx = bloco[idx_Q_pico] / amplitude

            menor_distancia = np.inf
            melhor_bits = ""

            for chave, ponto in self.constelacao.items():
                I = ponto["I"]
                Q = ponto["Q"]
                distancia = (I_rx-I)**2 + (Q_rx-Q)**2

                if distancia < menor_distancia:
                    menor_distancia = distancia
                    melhor_bits = chave

            bits += melhor_bits

        return bits


# Ruido Gaussiano
class Canal:
    def adicionar_ruido(self, sinal: np.ndarray, x: float = 0.0, sigma: float = 0.5) -> np.ndarray:
        ruido = np.random.normal(loc=x, scale=sigma, size=len(sinal))
        return sinal + ruido