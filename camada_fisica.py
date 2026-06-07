import numpy as np

class NRZ_POLAR():

    def modulation(self,voltageLevel:int,message:str):
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
        
            


        
        


if __name__ =="__main__":

    nrz_polar = NRZ_POLAR()
    nrz_polar.modulation(4,"ddddd")
    print("esse arquivo não é executavel")
