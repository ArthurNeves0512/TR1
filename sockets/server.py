import socket
import struct
import numpy as np


class Servidor:
    CABECALHO_TAMANHO = 4

    def __init__(self):
        self.callback = None
        self.sock = None

    def set_callback(self, callback):
        self.callback = callback

    def _receber_exatamente(self, conexao, quantidade):
        dados = bytearray()
        while len(dados) < quantidade:
            pacote = conexao.recv(quantidade - len(dados))
            if not pacote:
                return None
            dados.extend(pacote)
        return bytes(dados)

    def start(self, host="localhost", port=8082):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(3)

        print(f"Servidor iniciado na porta {port}")

        while True:
            client, address = self.sock.accept()
            print(f"Cliente conectado: {address}")

            try:
                cabecalho = self._receber_exatamente(client, self.CABECALHO_TAMANHO)
                if cabecalho is None:
                    raise ConnectionError("O cabeçalho do sinal não foi recebido por completo.")

                tamanho_dados = struct.unpack("!I", cabecalho)[0]
                if tamanho_dados <= 0:
                    raise ValueError("O sinal recebido está vazio.")
                if tamanho_dados % np.dtype(np.float32).itemsize != 0:
                    raise ValueError("O tamanho recebido não corresponde a valores float32.")

                dados = self._receber_exatamente(client, tamanho_dados)
                if dados is None:
                    raise ConnectionError("O sinal foi recebido de forma incompleta.")

                sinal = np.frombuffer(dados, dtype=np.float32).copy()
                print(f"Recebidas {len(sinal)} amostras float32.")

                if self.callback is not None:
                    self.callback(sinal)

            except Exception as erro:
                print(f"Erro no servidor: {erro}")
            finally:
                client.close()
                print("Conexão encerrada.")
