class CamadaEnlace:
    
    def __init__(self,config=None):
        self.config = config
        self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM = 4

    # Enquadramento

    

    def enquadramento_contagem_caracteres(self, dados_bits: str) -> str:
        # pega o tamanho em bytes da string de bits, então um 0000 11111 vai dar tamanho_dados = 1
        tamanho_dados = int(len(dados_bits)/8)
        #aqui é multiplicando por 8 para transformar em bits, apenas isso.
        cabecalho = format(tamanho_dados, f'0{self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM*8}b')
        quadro = cabecalho + dados_bits
        return quadro

    def desenquadramento_contagem_caracteres(self, quadro: str) -> str:
        cabecalho = quadro[:self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM*8]
        #indica que a string(vulgos os bits) então em base 2.
        tamanho_dados = int(cabecalho, 2)
        inicio_dados = self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM*8
        dados_originais = quadro[inicio_dados: inicio_dados + tamanho_dados*8]
        return dados_originais

    # ENQUADRAMENTO COM FLAGS e inserção de bytes ou caracteres
    
    FLAG_BYTE = '01111110'
    ESC_BYTE = '01111101'

    def enquadramento_insercao_bytes(self, dados_bits: str) -> str:

        quadro = ""
        quadro += self.FLAG_BYTE

        for i in range(0, len(dados_bits), 8):
            byte_atual = dados_bits[i:i+8]

            if byte_atual == self.FLAG_BYTE or byte_atual == self.ESC_BYTE:
                quadro += self.ESC_BYTE # Insere o ESC antes
            
            quadro += byte_atual # Adiciona o byte original
        quadro += self.FLAG_BYTE
        
        return quadro

    def desenquadramento_insercao_bytes(self, quadro: str) -> str:

        miolo_do_quadro = quadro[8:-8]
        mensagem_limpa = ""
        ignorar_proximo_esc = False

        for i in range(0, len(miolo_do_quadro), 8):
            byte_atual = miolo_do_quadro[i:i+8]
            
            if ignorar_proximo_esc:
                mensagem_limpa += byte_atual
                ignorar_proximo_esc = False
                
            elif byte_atual == self.ESC_BYTE:
                ignorar_proximo_esc = True
                
            else:
                mensagem_limpa += byte_atual

        return mensagem_limpa
    
    # ENQUADRAMENTO com FLAGS Inserção de bits

    def enquadramento_insercao_bits(self, dados_bits: str) -> str:

        FLAG_BITS = "01111110"
        quadro_final = ""
        contador_uns = 0
        quadro_final += FLAG_BITS
        
        for bit in dados_bits:
            quadro_final += bit

            if bit == '1':
                contador_uns += 1
            else:
                contador_uns = 0 
                
            if contador_uns == 5:
                quadro_final += '0'  
                contador_uns = 0  
        quadro_final += FLAG_BITS
        
        return quadro_final
    
    def desenquadramento_insercao_bits(self, quadro: str) -> str:

        miolo_do_quadro = quadro[8:-8]
        
        mensagem_limpa = ""
        contador_uns = 0
        
        for bit in miolo_do_quadro:
            if bit == '1':
                mensagem_limpa += bit
                contador_uns += 1
                
            else: 
                if contador_uns == 5:
                    contador_uns = 0
                else:
                    mensagem_limpa += bit
                    contador_uns = 0
                    
        return mensagem_limpa
    
    "Detecção de erros"
    # PARIDADE PAR

    def enquadramento_paridade_par(self, dados_bits: str) -> str:
    
        contador_uns = dados_bits.count('1')
        
        if contador_uns % 2 == 0:
            bit_paridade = '0'
        else:
            bit_paridade = '1'   
        quadro_final = dados_bits + bit_paridade

        return quadro_final

    def desenquadramento_paridade_par(self, quadro: str) -> str:

        contador_uns = quadro.count('1')
        
        if contador_uns % 2 != 0:
            print("ALERTA [RX]: Erro de paridade detectado! O quadro foi corrompido no canal.")#Apenas para teste, tirar depois

        dados_originais = quadro[:-1]
        
        return dados_originais

    #  CHECKSUM

    def _soma_blocos_8bits(self, dados_bits: str) -> int:
 
        resto = len(dados_bits) % 8
        if resto != 0:
            dados_bits = dados_bits.zfill(len(dados_bits) + (8 - resto))
        soma = 0

        for i in range(0, len(dados_bits), 8):
            bloco = dados_bits[i:i+8]
            soma += int(bloco, 2)

            if soma > 255:
                soma = (soma & 255) + 1
                
        return soma

    def enquadramento_checksum(self, dados_bits: str) -> str:
        
        soma = self._soma_blocos_8bits(dados_bits)
        checksum_int = soma ^ 255
        checksum_bits = format(checksum_int, '08b')

        return dados_bits + checksum_bits

    def desenquadramento_checksum(self, quadro: str) -> str:
  
        soma_total = self._soma_blocos_8bits(quadro)
        
        if soma_total != 255:
            print(" ALERTA [RX]: Erro de Checksum detectado! O quadro foi corrompido no canal.")#Apenas para teste, tirar depois

        dados_originais = quadro[:-8]
        
        return dados_originais

    # CRC-32 
    
    POLINOMIO_CRC32 = "100000100110000010001110110110111"

    def _calcula_crc(self, dados_bits: str, polinomio: str) -> str:

        grau = len(polinomio) - 1
        
        dados_padded = dados_bits + ('0' * grau)
        dados_lista = list(dados_padded)

        for i in range(len(dados_bits)):
            if dados_lista[i] == '1':
                for j in range(len(polinomio)):
                    bit_a = int(dados_lista[i+j])
                    bit_b = int(polinomio[j])
                    dados_lista[i+j] = str(bit_a ^ bit_b)
                    
        resto = ''.join(dados_lista[-grau:])
        return resto

    def enquadramento_crc(self, dados_bits: str) -> str:
     
        crc = self._calcula_crc(dados_bits, self.POLINOMIO_CRC32)
        
        return dados_bits + crc

    def desenquadramento_crc(self, quadro: str) -> str:
       
        resto = self._calcula_crc(quadro, self.POLINOMIO_CRC32)

        if '1' in resto:
            print("ALERTA [RX]: Erro de CRC detectado! Ruído no canal de comunicação.")#Apenas para teste, tirar depois
            
        dados_originais = quadro[:-32]
        
        return dados_originais
    
    "Correção de erros"
    # Protocolo decorreção de erro: Hamming

    def enquadramento_hamming(self, dados_bits: str) -> str:

        m = len(dados_bits)
        r = 0
        
        while (2**r) < (m + r + 1):
            r += 1
        quadro = ['0'] * (m + r)
        j = 0

        for i in range(1, m + r + 1):
            if (i & (i - 1)) != 0:
                quadro[i-1] = dados_bits[j]
                j += 1

        for i in range(r):
            pos = 2**i
            paridade = 0
            for j in range(1, m + r + 1):
                if j & pos:
                    paridade ^= int(quadro[j-1])
                    
            quadro[pos-1] = str(paridade)

        return ''.join(quadro)

    def desenquadramento_hamming(self, quadro: str) -> str:
        
        n = len(quadro)
        quadro_lista = list(quadro)
        sindrome = 0

        for i in range(1, n + 1):
            if quadro_lista[i-1] == '1':
                sindrome ^= i

        if sindrome != 0:
            print(f"ALERTA [RX]: Ruído corrompeu a posição {sindrome}!") # Apenas para teste, tirar depois
            print("[RX]: O Hamming está corrigindo o bit automaticamente...")#Apenas para teste, tirar depois

            if quadro_lista[sindrome-1] == '1':
                quadro_lista[sindrome-1] = '0'
            else:
                quadro_lista[sindrome-1] = '1'

        dados_originais = ""

        for i in range(1, n + 1):
            if (i & (i - 1)) != 0:
                dados_originais += quadro_lista[i-1]

        return dados_originais
    

if __name__ == "__main__":
    enlace = CamadaEnlace()
    
    # Nossa mensagem de 16 bits
    mensagem_bits = "1011100011111000"
    print(f"Mensagem original:  {mensagem_bits}")
    print("-" * 65)
    a = enlace.enquadramento_contagem_caracteres(mensagem_bits)
    print(a)
    print("-" * 65)
    b = enlace.desenquadramento_contagem_caracteres(a)
    print(b)
    