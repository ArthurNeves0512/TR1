import socket

class Servidor:
    def __init__(self):
        self.port=10
        self.server()

    def vamoPrintar(self):
        print("aaaaaaaaaa")

    def server(self,host="localhost",port=8082):
        maximo_de_dado = 2048
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address =(host,port)
        print(f"começando o servidor no {host.__str__}:{port}")
        sock.bind(server_address)
        sock.listen(3)
        i =0
        while(True):
            print("esperando dado")
            client,address = sock.accept()
            data = client.recv(maximo_de_dado)
            if data:
                print(f"Chegou isso aqui: {data.decode()}")
                client.send("Eu recebi do cliente".encode())
                client.close()
                i=i+1
                if(i>5):
                    break

if __name__ =='__main__':
    servidor = Servidor()
