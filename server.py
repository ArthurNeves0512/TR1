import socket
# Importe a classe que você criou
from camada_enlace import CamadaEnlace

class Servidor:
    def __init__(self):
        self.enlace = CamadaEnlace()
        
    # --- FUNÇÃO TRADUTORA (Aplicação) ---
    def bits_para_texto(self, bits: str) -> str:
        """Converte uma string de zeros e uns de volta para texto legível"""
        caracteres = [chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)]
        return ''.join(caracteres)
    
    def start(self, host="localhost", port=8082):
        maximo_de_dado = 2048
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_address = (host, port)
        print(f"Servidor ouvindo na porta: {port}")
        sock.bind(server_address)
        sock.listen(1)
        
        while True:
            print("\nEsperando conexão...")
            client_socket, address = sock.accept()
            
            try:
                # 1. Recebe os dados do canal (Socket)
                dados_recebidos = client_socket.recv(maximo_de_dado)
                if dados_recebidos:
                    quadro_recebido = dados_recebidos.decode('utf-8')
                    print(f"\n[Socket] Recebido do canal: {quadro_recebido}")
                    
                    # 2. Camada de Enlace RX (Desfazendo na ordem inversa: Desenquadra -> Checa CRC)
                    quadro_sem_flags = self.enlace.desenquadramento_insercao_bits(quadro_recebido)
                    dados_bits_limpos = self.enlace.desenquadramento_crc(quadro_sem_flags)
                    
                    print(f"[Enlace RX] Bits recuperados após auditoria: {dados_bits_limpos}")
                    
                    # 3. Camada de Aplicação (Bits -> Texto)
                    mensagem_final = self.bits_para_texto(dados_bits_limpos)
                    print(f"[Aplicação] MENSAGEM FINAL LIDA: {mensagem_final}")
                    
                    # Envia um OK de volta pro cliente
                    client_socket.send("Pacote recebido e processado com sucesso!".encode('utf-8'))
                    
            finally:
                client_socket.close()

if __name__ == '__main__':
    servidor = Servidor()
    servidor.start()