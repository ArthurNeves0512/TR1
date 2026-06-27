import numpy as np
import matplotlib.pyplot as plt

# Modulações digitais

class NrzPolar:
    def modulation(self, voltageLevel: float, bits_str: str) -> np.ndarray:
        voltage_stream = np.zeros(shape=(len(bits_str)),dtype=np.float32)
        for index, bit in enumerate(bits_str):
            voltage_stream[index] = voltageLevel if bit == '1' else -voltageLevel
        return voltage_stream

    def desmodulation(self, voltageLevel: float, voltage_stream: np.ndarray) -> str:
        bits = ''
        for voltage in voltage_stream:
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

    def desmodulation(self, voltageLevel: float, voltage_stream: np.ndarray) -> str:
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

    def desmodulation(self, voltageLevel: float, voltage_stream: np.ndarray) -> str:
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
        t = np.linspace(0, 1, self.amostras_por_bit, endpoint=False,dtype=np.float32),
        onda_portadora = amplitude * np.sin(2 * np.pi * self.fc * t)
        onda_morta = np.zeros(self.amostras_por_bit)

        sinal_transmitido = np.zeros(len(bits_str) * self.amostras_por_bit)
        
        for i, bit in enumerate(bits_str):
            idx_inicio = i * self.amostras_por_bit
            idx_fim = idx_inicio + self.amostras_por_bit
            sinal_transmitido[idx_inicio:idx_fim] = onda_portadora if bit == '1' else onda_morta

        return sinal_transmitido

    def desmodulation(self, amplitude: float, sinal_modulado: np.ndarray) -> str:
        bits_recuperados = ""
        t = np.linspace(0, 1, self.amostras_por_bit, endpoint=False)
        onda_referencia = np.sin(2 * np.pi * self.fc * t)

        energia_bit_um = amplitude * np.sum(onda_referencia ** 2)
        limiar = energia_bit_um / 2

        for i in range(0, len(sinal_modulado), self.amostras_por_bit):
            bloco_sinal = sinal_modulado[i:i + self.amostras_por_bit]
            correlacao = np.sum(bloco_sinal * onda_referencia)
            bits_recuperados += '1' if correlacao > limiar else '0'

        return bits_recuperados

class FSK:
    def __init__(self, amostras_por_bit=200, fc0=2, fc1=5):
        self.amostras_por_bit = amostras_por_bit
        self.fc0 = fc0
        self.fc1 = fc1

    def modulation(self, amplitude: float, bits_str: str) -> np.ndarray:
        t = np.linspace(0, 1, self.amostras_por_bit, endpoint=False,dtype=np.float32)
        onda_0 = amplitude * np.sin(2 * np.pi * self.fc0 * t)
        onda_1 = amplitude * np.sin(2 * np.pi * self.fc1 * t)

        sinal_transmitido = np.zeros(len(bits_str) * self.amostras_por_bit)
        
        for i, bit in enumerate(bits_str):
            idx_inicio = i * self.amostras_por_bit
            idx_fim = idx_inicio + self.amostras_por_bit
            sinal_transmitido[idx_inicio:idx_fim] = onda_1 if bit == '1' else onda_0

        return sinal_transmitido

    def desmodulation(self, amplitude: float, sinal_modulado: np.ndarray) -> str:
        bits_recuperados = ""
        # Como o t vai de 0 a 1 segundo, a frequencia de amostragem (fs) e igual ao numero de amostras
        fs = self.amostras_por_bit 

        for i in range(0, len(sinal_modulado), self.amostras_por_bit):
            bloco_sinal = sinal_modulado[i:i + self.amostras_por_bit]
            
            # Aplica a Transformada de Fourier
            fft_result = np.fft.fft(bloco_sinal)
            freqs = np.fft.fftfreq(len(bloco_sinal), d=1/fs)
            
            # Pega apenas a parte positiva do espectro
            metade = len(freqs) // 2
            espectro_positivo = np.abs(fft_result[:metade])
            freqs_positivas = freqs[:metade]
            
            # Encontra a frequencia com a maior magnitude (pico)
            idx_pico = np.argmax(espectro_positivo)
            freq_predominante = freqs_positivas[idx_pico]
            
            # Decide o bit pela proximidade com as portadoras
            if abs(freq_predominante - self.fc1) < abs(freq_predominante - self.fc0):
                bits_recuperados += '1'
            else:
                bits_recuperados += '0'

        return bits_recuperados

class QPSK:
    def __init__(self, amostras_por_simbolo=200, fc=2):
        self.amostras_por_simbolo = amostras_por_simbolo
        self.fc = fc
        self.fases = {
            '00': np.pi / 4,
            '01': 3 * np.pi / 4,
            '11': 5 * np.pi / 4,
            '10': 7 * np.pi / 4,
        }

    def modulation(self, amplitude: float, bits_str: str) -> np.ndarray:
        if len(bits_str) % 2 != 0:
            bits_str += '0'

        t = np.linspace(0, 1, self.amostras_por_simbolo, endpoint=False,dtype=np.float32)
        num_simbolos = len(bits_str) // 2
        sinal_transmitido = np.zeros(num_simbolos * self.amostras_por_simbolo)

        for j, i in enumerate(range(0, len(bits_str), 2)):
            dibit = bits_str[i:i + 2]
            fase = self.fases[dibit]
            onda = amplitude * np.sin(2 * np.pi * self.fc * t + fase)
            
            idx_inicio = j * self.amostras_por_simbolo
            idx_fim = idx_inicio + self.amostras_por_simbolo
            sinal_transmitido[idx_inicio:idx_fim] = onda

        return sinal_transmitido

    def desmodulation(self, amplitude: float, sinal_modulado: np.ndarray) -> str:
        bits_recuperados = ""
        t = np.linspace(0, 1, self.amostras_por_simbolo, endpoint=False,dtype=np.float32)

        for i in range(0, len(sinal_modulado), self.amostras_por_simbolo):
            bloco_sinal = sinal_modulado[i:i + self.amostras_por_simbolo]

            correlacao_i = np.sum(bloco_sinal * np.sin(2 * np.pi * self.fc * t))
            correlacao_q = np.sum(bloco_sinal * np.cos(2 * np.pi * self.fc * t))

            angulo = np.arctan2(correlacao_q, correlacao_i)
            if angulo < 0:
                angulo += 2 * np.pi

            dibit_recuperado = min(self.fases.keys(), key=lambda k: abs(angulo - self.fases[k]))
            bits_recuperados += dibit_recuperado

        return bits_recuperados

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

    def desmodulation(self, amplitude_base: float, sinal_modulado: np.ndarray) -> str:
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
"""if __name__ == '__main__':
    # Configurações de teste
    bits_originais = "10110010" # 8 bits é perfeito pois é divisível por 2 (QPSK) e 4 (16-QAM)
    tensao = 1.0
    sigma_ruido = 0.5 
    canal = Canal()
    
    # Dicionario para armazenar resultados de todas as modulacoes
    resultados = {}

    # 1. Baseband Modulations
    baseband_mods = {'NRZ-Polar': NrzPolar(), 'Manchester': Manchester(), 'Bipolar': Bipolar()}
    for nome, mod in baseband_mods.items():
        sinal_tx = mod.modulation(tensao, bits_originais)
        sinal_rx = canal.adicionar_ruido(sinal_tx, sigma=sigma_ruido)
        bits_rx = mod.desmodulation(tensao, sinal_rx)
        resultados[nome] = {'tx': sinal_tx, 'rx': sinal_rx, 'bits': bits_rx, 'is_base': True}

    # 2. Carrier Modulations
    carrier_mods = {'ASK': ASK(), 'FSK': FSK(), 'QPSK': QPSK(), '16-QAM': QAM16()}
    for nome, mod in carrier_mods.items():
        sinal_tx = mod.modulation(tensao, bits_originais)
        sinal_rx = canal.adicionar_ruido(sinal_tx, sigma=sigma_ruido)
        bits_rx = mod.desmodulation(tensao, sinal_rx)
        resultados[nome] = {'tx': sinal_tx, 'rx': sinal_rx, 'bits': bits_rx, 'is_base': False}

    # --- Plotagem de todos os testes ---
    fig, axes = plt.subplots(7, 2, figsize=(16, 22))
    fig.suptitle(f"Dashboard Camada Física | Bits Iniciais: {bits_originais} | Ruído \u03C3={sigma_ruido}", fontsize=18)

    for idx, (nome, data) in enumerate(resultados.items()):
        ax_tx = axes[idx, 0]
        ax_rx = axes[idx, 1]
        
        sinal_tx, sinal_rx, bits_rx, is_base = data['tx'], data['rx'], data['bits'], data['is_base']
        
        cor_erro = 'green' if bits_rx == bits_originais else 'red'
        
        # Plot TX
        ax_tx.set_title(f"{nome} TX")
        if is_base:
            ax_tx.step(np.arange(len(sinal_tx)), sinal_tx, where='post', color='blue', linewidth=2)
            ax_tx.set_ylim(-tensao * 1.5, tensao * 1.5)
        else:
            x_val = np.linspace(0, len(bits_originais), len(sinal_tx), endpoint=False)
            ax_tx.plot(x_val, sinal_tx, color='blue', linewidth=1.5)
            # Para o 16-QAM, o sinal pode chegar a 3 * 1.41 * amplitude
            y_lim = tensao * 4.5 if nome == '16-QAM' else tensao * 1.5
            ax_tx.set_ylim(-y_lim, y_lim)
        ax_tx.grid(True)

        # Plot RX
        ax_rx.set_title(f"{nome} RX | Recebido: {bits_rx}", color=cor_erro, fontweight='bold')
        if is_base:
            x_base = np.arange(len(sinal_rx))
            ax_rx.plot(x_base, sinal_rx, color='red', alpha=0.6)
            ax_rx.step(x_base, sinal_tx, where='post', color='black', linestyle='--', alpha=0.5)
            ax_rx.set_ylim(-tensao * 2.5, tensao * 2.5)
        else:
            x_val = np.linspace(0, len(bits_originais), len(sinal_rx), endpoint=False)
            ax_rx.plot(x_val, sinal_rx, color='red', alpha=0.6)
            ax_rx.plot(x_val, sinal_tx, color='black', linestyle='--', alpha=0.4)
            y_lim = tensao * 5.5 if nome == '16-QAM' else tensao * 2.5
            ax_rx.set_ylim(-y_lim, y_lim)
        ax_rx.grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.97]) # Espaço para o Suptitle
    plt.show()

    print("\nResumo da Decodificação:")
    print("-" * 30)
    for nome, data in resultados.items():
        status = "OK" if data['bits'] == bits_originais else "ERRO"
        print(f"{nome.ljust(12)} -> {data['bits']} [{status}]")"""