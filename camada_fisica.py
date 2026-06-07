import numpy as np

class NRZ_POLAR():

    def modulation(self,voltageLevel:int,message:str):
        hex_message = message.encode('utf-8')
        bit_stream=np.zeros(len(hex_message),dtype=int)

        for index, byte in 
        for index,bit in enumerate(bit_stream):
            if(bit==1):
                bit_stream[index]=10
        # for indice,bit in enumerate(bit_stream):
        

        # print(f"final: {bit_stream}")

        
            


        
        


if __name__ =="__main__":

    nrz_polar = NRZ_POLAR()
    nrz_polar.modulation(4,"Hello")
    print("esse arquivo não é executavel")
