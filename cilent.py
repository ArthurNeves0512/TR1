import socket
from servidor import Servidor


class Cliente:
    def __init__(self):
        print("a")

        self.init_client()
    
    def init_client(self,host='localhost',port=8082):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_address = (host,port)
        sock.connect(server_address)
        try:
            message = "Opa meu personagem moveu"
            print(f"string: {message}")
            print("Enviando...............")
            sock.send(message.encode('utf-8'))
            sock.close()
        except socket.error as e: 
            print ("Socket error: %s" %str(e)) 



if __name__ =="__main__":
    cliente = Cliente()


