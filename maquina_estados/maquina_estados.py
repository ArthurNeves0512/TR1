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
        

    def execute(self):
        print("---------------------------------------------------------------")
        print(camada_enlace.CamadaEnlace().enquadramento_contagem_caracteres(self.msg))
        print("---------------------------------------------------------------")
        return self.execute_digital_modulation()

    def receving(self,array):
        return camada_fisica.NrzPolar().desmodulation(voltageLevel=4,voltage_stream=array)

    def execute_digital_modulation(self)->np.array:
        voltage_level = int(self.config['voltage_level'])
        if(self.config['digital_modulation']=='Nrz Polar'):
            return camada_fisica.NrzPolar().modulation(voltageLevel=voltage_level,bits_str=self.msg)
        if(self.config['digital_modulation']=='Bipolar'):
            return camada_fisica.Bipolar().modulation(voltageLevel=voltage_level,bits_str=self.msg)
        if(self.config['digital_modulation']=='Manchester'):
            return camada_fisica.Manchester().modulation(voltageLevel=voltage_level,bits_str=self.msg)

    def execute_analog_modulation(self):
        pass