from codigo_fisica import camada_fisica
import numpy as np
from codigo_enlace import camada_enlace
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
def plot_sinal_analogico(sinal, amostras_por_bit=200, titulo="Sinal Modulado"):

    sinal = np.asarray(sinal)

    plt.figure(figsize=(12, 3))
    plt.plot(sinal, linewidth=1.5)

    for i in range(0, len(sinal), amostras_por_bit):
        plt.axvline(i, color="gray", linestyle="--", alpha=0.3)

    plt.title(titulo)
    plt.xlabel("Amostras")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    


def plot_sinal_digital(sinal, titulo="Sinal Digital", amostras_por_bit=None):
    sinal = np.asarray(sinal)

    x = np.arange(len(sinal) + 1)
    y = np.append(sinal, sinal[-1])

    plt.figure(figsize=(12, 3))
    plt.step(x, y, where="post")

    if amostras_por_bit is not None:
        for i in range(0, len(sinal), amostras_por_bit):
            plt.axvline(i, color="gray", linestyle="--", alpha=0.4)

    plt.title(titulo)
    plt.xlabel("Amostras")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    
def desenhar_quadro(bits, campos,titulo):
 
    fig, ax = plt.subplots(figsize=(len(bits)*0.35,2.8))
    ax.set_title(titulo, fontsize=16)
    for i, bit in enumerate(bits):

        cor = "white"

        for nome, ini, fim, c in campos:
            if ini <= i < fim:
                cor = c
                break

        ax.add_patch(Rectangle(
            (i,0),
            1,
            1,
            facecolor=cor,
            edgecolor="black"
        ))

        ax.text(
            i+0.5,
            0.5,
            bit,
            ha="center",
            va="center",
            fontsize=12
        )

    for nome, ini, fim, cor in campos:

        meio = (ini+fim)/2

        ax.text(
            meio,
            -0.25,
            nome,
            ha="center",
            fontsize=12,
            color="black"
        )

    ax.set_xlim(0,len(bits))
    ax.set_ylim(-0.6,1.2)

    ax.set_xticks(range(len(bits)+1))
    ax.set_yticks([])

    plt.grid(axis="x")
    


class BitConverter:

    def __init__(self):
        pass

    def text_to_bits(self,text: str) -> str:
        return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

    
    def bits_to_text(self, bits: str) -> str:
        bits = bits[:len(bits) - (len(bits) % 8)]

        data = bytearray()

        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            try:
                data.append(int(byte, 2))
            except ValueError:
                continue

        return data.decode('utf-8', errors='replace')


class MaquinaEstados():
    def __init__(self,config,msg:str):
        self.config = config
        self.msg = msg
        

    def sending(self):
        media_erro = self.config['media_erro']
        sigma_erro = self.config['sigma_erro']
        msg_enquadrada = self.execute_framming(self.msg,True)
        msg_modulation= self.execute_modulation(msg_enquadrada,True)
        plt.show()
        msg_modulation = camada_enlace.Canal(media_erro,sigma_erro).transmitir(msg_modulation)
        return msg_modulation
    
    def receving(self,array:np.array):
        msg_desmodularizada = self.execute_modulation(array,False)
        msg_desenquadrada = self.execute_framming(msg_desmodularizada,False)
        return BitConverter().bits_to_text(msg_desenquadrada)


    def execute_framming(self,bits_str,isSending:bool)->str:
        enlace =camada_enlace.CamadaEnlace(self.config)
        metodo_framming = self.config['framming_type']
        if(metodo_framming=='Contagem de Caracteres'):
            tamanho_em_bits_frame = self.config['frame_size']*8
            if(isSending): 
                result = enlace.enquadramento_contagem_caracteres(bits_str)
                campos = [
                ("Cabeçalho",0,tamanho_em_bits_frame,"skyblue"),
                ("Dados",tamanho_em_bits_frame,len(result),"lightgreen")
                ]
                desenhar_quadro(result, campos,"Enquadramento por contagem de caracteres")
                return result
            return enlace.desenquadramento_contagem_caracteres(bits_str)
        if(metodo_framming=='Inserção Bytes'):
            if(isSending):
                result = enlace.enquadramento_insercao_bytes(bits_str)
                campos = [
                ("Cabeçalho inicio",0,8,"skyblue"),
                ("Dados",8,len(result)-8,"lightgreen"),
                ("Cabeçalho final",len(result)-8,len(result),"skyblue"),
                ]
                desenhar_quadro(result, campos,"Enquadramento por inserção de bytes")
                return result
            return enlace.desenquadramento_insercao_bytes(bits_str)
        if(metodo_framming=='Inserção Bits'):
            if(isSending):
                result =enlace.enquadramento_insercao_bits(bits_str)
                campos = [
                ("Cabeçalho inicio",0,8,"skyblue"),
                ("Dados",8,len(result)-8,"lightgreen"),
                ("Cabeçalho final",len(result)-8,len(result),"skyblue"),
                ]
                desenhar_quadro(result, campos,"Enquadramento por inserção de bits")
                return result
            return enlace.desenquadramento_insercao_bits(bits_str)
        
    def execute_modulation(self,bits_str,isSending:bool)->np.array:
        voltage_level = int(self.config['voltage_level'])
        modulation = self.config['modulation']
        if(modulation=='Nrz Polar'):
            if(isSending):
                result = camada_fisica.NrzPolar().modulation(voltageLevel=voltage_level,bits_str=bits_str)
                plot_sinal_digital(result,"NRZ Polar")
                return result
            return camada_fisica.NrzPolar().demodulation(voltageLevel=voltage_level,voltage_stream=bits_str)
        elif(modulation=='Bipolar'):
            if(isSending):
                result= camada_fisica.Bipolar().modulation(voltageLevel=voltage_level,bits_str=bits_str)
                plot_sinal_digital(result,"Bipolar")
                return result
            return camada_fisica.Bipolar().demodulation(voltageLevel=voltage_level,voltage_stream=bits_str)
        elif(modulation=='Manchester'):
            if(isSending):
                result = camada_fisica.Manchester().modulation(voltageLevel=voltage_level,bits_str=bits_str)
                plot_sinal_digital(result,"Manchester")
                return result
            return camada_fisica.Manchester().demodulation(voltageLevel=voltage_level,voltage_stream=bits_str)
        elif(modulation =='ASK'):
            if(isSending):
                result =  camada_fisica.ASK(amostras_por_bit=200).modulation(self.config['voltage_level'],bits_str=bits_str)
                plot_sinal_analogico(result,amostras_por_bit=200,titulo="AFK")
                return result
            return camada_fisica.ASK().demodulation(amplitude=self.config['voltage_level'],sinal_modulado=bits_str)
        elif(modulation =='FSK'):
            if(isSending):
                result =  camada_fisica.FSK().modulation(self.config['voltage_level'],bits_str=bits_str)
                plot_sinal_analogico(result,titulo="FSK")
                return result
            return camada_fisica.FSK().demodulation(amplitude=self.config['voltage_level'],sinal_modulado=bits_str)
        elif(modulation =='QPSK'):
            if(isSending):
                result = camada_fisica.QPSK().modulation(self.config['voltage_level'],bits_str=bits_str)
                plot_sinal_analogico(result,titulo="QPSK")
                return result
            return camada_fisica.QPSK().demodulation(bits_str)
        elif(modulation =='16-QAM'):
            if(isSending):
                result =  camada_fisica.QAM16().modulation(self.config['voltage_level'],bits_str=bits_str)
                plot_sinal_analogico(result,titulo="16-QAM")
                return result
            return camada_fisica.QAM16().demodulation(self.config['voltage_level'],bits_str=bits_str)
        
