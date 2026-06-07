import socket
from server import Servidor


class Cliente:
    def __init__(self):
        pass
    
    def send_message(self,host='localhost',port=8082,message=''):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_address = (host,port)
        sock.connect(server_address)
        try:
            print(f"string: {message}")
            print("Enviando...............")
            sock.send(message.encode('utf-8'))
            sock.close()
        except socket.error as e: 
            print ("Socket error: %s" %str(e)) 



if __name__ =="__main__":
    cliente = Cliente()

