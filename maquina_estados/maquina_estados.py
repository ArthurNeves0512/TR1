from codigo_fisica import camada_fisica
import numpy as np
from codigo_enlace import camada_enlace
class BitConverter:

    def __init__(self):
        pass

    def text_to_bits(self,text: str) -> str:
        return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

    def bits_to_text(self,bits: str) -> str:
        data = bytearray()

        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]

            if len(byte) < 8:
                break

            data.append(int(byte, 2))

        return data.decode('utf-8')


class MaquinaEstados():
    def __init__(self,config,msg:str):
        self.config = config
        self.msg = msg
        

    def sending(self):
        print("---------------------------------------------------------------")
        msg_enquadrada = self.execute_framming(self.msg,True)
        print(msg_enquadrada)
        print("---------------------------------------------------------------")
        msg_digital_modulation= self.execute_digital_modulation(msg_enquadrada,True)
        # print("AQUI A MSG DEPOIS DE FAZER O DIGITAL",msg_digital_modulation)
        print("FAZENDO ANALOG ---------------------------------------------------------------")
        a = self.execute_analog_modulation(msg_enquadrada,True)
        # print(a)
        print("FIZ ANALOG---------------------------------------------------------------")
        return msg_digital_modulation
    
    def receving(self,array:np.array):
        print("chegou isso aqui para desmodularizar", array)
        # msg_desmodularizada = self.execute_analog_modulation(array,False)    
        # print("esses são os bits desmodularizados",msg_desmodularizada)
        msg_desmodularizada = self.execute_digital_modulation(array,False)
        msg_desenquadrada = self.execute_framming(msg_desmodularizada,False)
        return BitConverter().bits_to_text(msg_desenquadrada)


    def execute_framming(self,bits_str,isSending:bool)->str:
        metodo_framming = self.config['framming_type']
        if(metodo_framming=='Contagem de Caracteres'):
            if(isSending):
                return camada_enlace.CamadaEnlace().enquadramento_contagem_caracteres(bits_str)
            return camada_enlace.CamadaEnlace().desenquadramento_contagem_caracteres(bits_str)
        if(metodo_framming=='Inserção Bytes'):
            if(isSending):
                return camada_enlace.CamadaEnlace().enquadramento_insercao_bytes(bits_str)
            return camada_enlace.CamadaEnlace().desenquadramento_insercao_bytes(bits_str)
        if(metodo_framming=='Inserção Bits'):
            if(isSending):
                print("eu entrei aqui")
                return camada_enlace.CamadaEnlace().enquadramento_insercao_bits(bits_str)
            return camada_enlace.CamadaEnlace().desenquadramento_insercao_bits(bits_str)
        


    def execute_digital_modulation(self,bits_str,isSending:bool)->np.array:
        voltage_level = int(self.config['voltage_level'])
        if(self.config['digital_modulation']=='Nrz Polar'):
            if(isSending):
                return camada_fisica.NrzPolar().modulation(voltageLevel=voltage_level,bits_str=bits_str)
            return camada_fisica.NrzPolar().desmodulation(voltageLevel=voltage_level,voltage_stream=bits_str)
        if(self.config['digital_modulation']=='Bipolar'):
            if(isSending):
                return camada_fisica.Bipolar().modulation(voltageLevel=voltage_level,bits_str=bits_str)
            return camada_fisica.Bipolar().desmodulation(voltageLevel=voltage_level,voltage_stream=bits_str)
        if(self.config['digital_modulation']=='Manchester'):
            if(isSending):
                return camada_fisica.Manchester().modulation(voltageLevel=voltage_level,bits_str=bits_str)
            return camada_fisica.Manchester().desmodulation(voltageLevel=voltage_level,voltage_stream=bits_str)

    def execute_analog_modulation(self,bits,isSending:bool):
        analog_modulation = self.config['analog_modulation']
        if(analog_modulation =='ASK'):
            if(isSending):
                return camada_fisica.ASK().modulation(self.config['voltage_level'],bits_str=bits)
            return camada_fisica.ASK().desmodulation(amplitude=self.config['voltage_level'],sinal_modulado=bits)
        if(analog_modulation =='FSK'):
            if(isSending):
                return camada_fisica.FSK().modulation(self.config['voltage_level'],bits_str=bits)
            return camada_fisica.FSK().desmodulation(amplitude=self.config['voltage_level'],sinal_modulado=bits)
        if(analog_modulation =='QPSK'):
            if(isSending):
                return camada_fisica.QPSK().modulation(self.config['voltage_level'],bits_str=bits)
            return camada_fisica.QPSK().desmodulation(amplitude=self.config['voltage_level'],sinal_modulado=bits)
        if(analog_modulation =='16-QAM'):
            if(isSending):
                return camada_fisica.QAM16().modulation(self.config['voltage_level'],bits_str=bits)
            return camada_fisica.QAM16().desmodulation(amplitude=self.config['voltage_level'],sinal_modulado=bits)
        pass
