import socket
import numpy as np


class Servidor:
    def __init__(self):
        self.callback = None
        self.sock = None

    def set_callback(self, callback):
        self.callback = callback

    def start(self, host="localhost", port=8082):
        BUFFER_SIZE = 4096

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((host, port))
        self.sock.listen(3)

        print(f"Servidor iniciado na porta {port}")

        while True:

            print("Esperando conexão...")

            client, address = self.sock.accept()

            print(f"Cliente conectado: {address}")

            try:
                print("to aqui?")
                dados = bytearray()

                while True:

                    pacote = client.recv(BUFFER_SIZE)

                    if not pacote:
                        break

                    dados.extend(pacote)

                print(f"Recebidos {len(dados)} bytes.")

                # Se estiver enviando um numpy.ndarray
                sinal = np.frombuffer(dados, dtype=np.float32)

                print(sinal)

                if self.callback is not None:
                    self.callback(sinal)

            except Exception as e:
                print(e)

            finally:
                client.close()
                print("Conexão encerrada.")


if __name__ == "__main__":
    servidor = Servidor()
    servidor.start()