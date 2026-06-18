import socket
import socket


class Servidor:
    def __init__(self):
        self.callback = None
        self.sock = None

    def set_callback(self, callback):
        """
        Registra uma função que será chamada sempre
        que novos dados chegarem.
        """
        self.callback = callback

    def start(self, host="localhost", port=8082):
        maximo_de_dado = 2048

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_address = (host, port)

        print(f"Começando o servidor na porta {port}")

        self.sock.bind(server_address)
        self.sock.listen(3)

        while True:
            print("Esperando conexão...")

            client, address = self.sock.accept()

            print(f"Cliente conectado: {address}")

            try:
                data = client.recv(maximo_de_dado)

                if data:
                    print(f"Chegou isso aqui: {data.decode()}")

                    # avisa quem estiver interessado
                    if self.callback is not None:
                        self.callback(data)

                    # ecoa os dados de volta para o cliente
                    client.sendall(data)

            except Exception as e:
                print(f"Erro ao receber dados: {e}")

            finally:
                client.close()
                print("Conexão encerrada")


if __name__=='__main__':
    servidor = Servidor()
    servidor.start()