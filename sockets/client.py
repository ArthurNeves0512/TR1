import socket

from codigo_enlace import camada_enlace  
from codigo_fisica import camada_fisica

class Cliente:
    def __init__(self):
        self.enlace = camada_enlace.CamadaEnlace()
    
    # --- FUNÇÃO TRADUTORA (Aplicação) ---
    def texto_para_bits(self, texto: str) -> str:
        """Converte uma string de texto em uma string de zeros e uns (ASCII)"""
        bits = ''.join(format(ord(letra), '08b') for letra in texto)
        return bits

    def send_message(self, mensage:str,host='localhost', port=8082):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, port)
        sock.connect(server_address)
        
        try:
            # 1. Pega a mensage do usuário via terminal
            
            # 2. Camada de Aplicação (Texto -> Bits)
            dados_bits = self.texto_para_bits(mensage)
            print(f"[Aplicação] Bits gerados: {dados_bits}")
            
            # 3. Camada de Enlace TX (Vamos usar Inserção de Bits + CRC como exemplo)
            quadro_com_erro = self.enlace.enquadramento_crc(dados_bits)
            quadro_final = self.enlace.enquadramento_insercao_bits(quadro_com_erro)
            
            print(f"[Enlace TX] Quadro blindado gerado: {quadro_final}")
            print("Enviando pelo socket...............")
            
            # 4. Envia para o Servidor (O Socket só aceita bytes, então encodamos a string de bits)
            sock.send(quadro_final.encode('utf-8'))
            
            # Recebe a resposta do servidor para saber se chegou bem
            resposta = sock.recv(2048)
            print(f"[Servidor Respondeu]: {resposta.decode()}")
            
        except socket.error as e: 
            print("Socket error: %s" % str(e)) 
        finally:
            sock.close()

if __name__ == "__main__":
    cliente = Cliente()
    cliente.send_message()
    aa = "a"
    
    msgA = camada_fisica.NrzPolar().modulation(4,aa)
    cliente.send_message(message=msgA)

