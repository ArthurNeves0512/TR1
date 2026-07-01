import socket
import struct
import numpy as np


class Cliente:
    CABECALHO_TAMANHO = 4

    def send_message(self, array, host="localhost", port=8082):
        sinal = np.asarray(array, dtype=np.float32)
        dados = sinal.tobytes()
        cabecalho = struct.pack("!I", len(dados))

        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                sock.sendall(cabecalho)
                sock.sendall(dados)
            return True, None
        except OSError as erro:
            mensagem = f"Não foi possível enviar o sinal: {erro}"
            print(mensagem)
            return False, mensagem
