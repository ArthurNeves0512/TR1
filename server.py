import socket

class Servidor:
    def __init__(self):
        pass


    def start(self,host="localhost",port=8082):
        maximo_de_dado = 2048
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address =(host,port)
        print(f"começando o servidor na porta:{port}")
        sock.bind(server_address)
        sock.listen(3)
        while(True):
            print("esperando dado")
            client,address = sock.accept()
            data = client.recv(maximo_de_dado)
            if data:
                print(f"Chegou isso aqui: {data.decode()}")
                client.send("Eu recebi do cliente e".encode())
            

if __name__ =='__main__':
    servidor = Servidor()
    servidor.start()
