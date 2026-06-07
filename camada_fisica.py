import numpy as np


class NrzPolar:

    def modulation(self,voltageLevel:int,message:str)->np.ndarray:
        message = message.encode('utf-8')
        bits=''
        for hex in message:
            bits = bits+format(hex,'08b')

        voltage_stream=np.zeros(shape=(len(bits)))
        
        for index,bit in enumerate(bits):
            if(bit =='0'):
                voltage_stream[index]=-voltageLevel
            else:
                voltage_stream[index]=voltageLevel

        return voltage_stream

    def desmodulation(self,voltageLevel:int,message:str)->np.ndarray:
        pass
        
class Bipolar():

    def modulation(self,voltageLevel:int,message:str)->np.ndarray:
        message = message.encode('utf-8')
        bits=''
        count_hight_bits=0
        for hex in message:
            bits=bits+format(hex,'08b')
        voltage_stream = np.zeros(shape=(len(bits)))
        for index,bit in enumerate(bits):
            if(bit=='1'):
                if(count_hight_bits%2!=0):
                    voltage_stream[index]=-voltageLevel
                else:
                    voltage_stream[index]=voltageLevel
                count_hight_bits+=1
        return voltage_stream
        
    
    def desmodulation():
        pass
        
        


if __name__ =="__main__":

    nrz_polar = NrzPolar()
    nrz_polar.modulation(4,"ddddd")

    bipolar = Bipolar()
    print(bipolar.modulation(4,'hello'))
    print("esse arquivo não é executavel")
