class CamadaEnlace:
    
    def __init__(self, config=None):
        self.config = config
        self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM = 4

    def _validar_bits(self, bits: str) -> bool:
        return isinstance(bits, str) and bits != "" and all(bit in "01" for bit in bits)

    # Enquadramento

    def enquadramento_contagem_caracteres(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")

        if len(dados_bits) % 8 != 0:
            raise ValueError("A contagem de caracteres exige uma quantidade inteira de bytes.")

        # Pega o tamanho da carga útil em bytes.
        tamanho_dados = len(dados_bits) // 8

        # O cabeçalho possui 4 bytes, ou seja, 32 bits.
        cabecalho = format(
            tamanho_dados,
            f'0{self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM * 8}b'
        )

        quadro = cabecalho + dados_bits
        return quadro

    def desenquadramento_contagem_caracteres(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro):
            return None, "Erro de Transmissão"

        tamanho_cabecalho = self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM * 8

        if len(quadro) < tamanho_cabecalho:
            return None, "Erro de Transmissão"

        cabecalho = quadro[:tamanho_cabecalho]
        tamanho_dados = int(cabecalho, 2)
        inicio_dados = tamanho_cabecalho
        fim_dados = inicio_dados + tamanho_dados * 8

        if len(quadro) < fim_dados:
            return None, "Erro de Transmissão"

        if len(quadro) > fim_dados:
            return None, "Erro de Transmissão"

        dados_originais = quadro[inicio_dados:fim_dados]
        return dados_originais, None

    # ENQUADRAMENTO COM FLAGS e inserção de bytes ou caracteres
    
    FLAG_BYTE = '01111110'
    ESC_BYTE = '01111101'

    def enquadramento_insercao_bytes(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")

        if len(dados_bits) % 8 != 0:
            raise ValueError("A inserção de bytes exige uma quantidade inteira de bytes.")

        quadro = ""
        quadro += self.FLAG_BYTE

        for i in range(0, len(dados_bits), 8):
            byte_atual = dados_bits[i:i+8]

            if byte_atual == self.FLAG_BYTE or byte_atual == self.ESC_BYTE:
                quadro += self.ESC_BYTE  # Insere o ESC antes.
            
            quadro += byte_atual  # Adiciona o byte original.

        quadro += self.FLAG_BYTE
        return quadro

    def desenquadramento_insercao_bytes(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro):
            return None, "Erro de Transmissão"

        if len(quadro) < 16:
            return None, "Erro de Transmissão"

        if len(quadro) % 8 != 0:
            return None, "Erro de Transmissão"

        if not quadro.startswith(self.FLAG_BYTE) or not quadro.endswith(self.FLAG_BYTE):
            return None, "Erro de Transmissão"

        miolo_do_quadro = quadro[8:-8]
        mensagem_limpa = ""
        ignorar_proximo_esc = False

        for i in range(0, len(miolo_do_quadro), 8):
            byte_atual = miolo_do_quadro[i:i+8]
            
            if ignorar_proximo_esc:
                if byte_atual != self.FLAG_BYTE and byte_atual != self.ESC_BYTE:
                    return None, "Erro de Transmissão"

                mensagem_limpa += byte_atual
                ignorar_proximo_esc = False
                
            elif byte_atual == self.ESC_BYTE:
                ignorar_proximo_esc = True
                
            elif byte_atual == self.FLAG_BYTE:
                return None, "Erro de Transmissão"

            else:
                mensagem_limpa += byte_atual

        if ignorar_proximo_esc:
            return None, "Erro de Transmissão"

        return mensagem_limpa, None
    
    # ENQUADRAMENTO com FLAGS Inserção de bits

    def enquadramento_insercao_bits(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")

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
    
    def desenquadramento_insercao_bits(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro):
            return None, "Erro de Transmissão"

        FLAG_BITS = "01111110"

        if len(quadro) < 16:
            return None, "Erro de Transmissão"

        if not quadro.startswith(FLAG_BITS) or not quadro.endswith(FLAG_BITS):
            return None, "Erro de Transmissão"

        miolo_do_quadro = quadro[8:-8]
        mensagem_limpa = ""
        contador_uns = 0
        i = 0
        
        while i < len(miolo_do_quadro):
            bit = miolo_do_quadro[i]

            if bit == '1':
                mensagem_limpa += bit
                contador_uns += 1

                if contador_uns == 5:
                    if i + 1 >= len(miolo_do_quadro):
                        return None, "Erro de Transmissão"

                    if miolo_do_quadro[i + 1] != '0':
                        return None, "Erro de Transmissão"

                    # Pula o zero inserido pelo transmissor.
                    i += 1
                    contador_uns = 0
            else:
                mensagem_limpa += bit
                contador_uns = 0

            i += 1

        return mensagem_limpa, None
    
    # Detecção de erros

    # PARIDADE PAR

    def enquadramento_paridade_par(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")

        contador_uns = dados_bits.count('1')
        
        if contador_uns % 2 == 0:
            bit_paridade = '0'
        else:
            bit_paridade = '1'

        quadro_final = dados_bits + bit_paridade
        return quadro_final

    def desenquadramento_paridade_par(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro):
            return None, "Erro de Transmissão"

        if len(quadro) < 2:
            return None, "Erro de Transmissão"

        contador_uns = quadro.count('1')
        
        if contador_uns % 2 != 0:
            return None, "Erro de Transmissão"

        dados_originais = quadro[:-1]
        return dados_originais, None

    # CHECKSUM

    def _soma_blocos_8bits(self, dados_bits: str) -> int:
        resto = len(dados_bits) % 8

        if resto != 0:
            dados_bits = dados_bits.zfill(len(dados_bits) + (8 - resto))

        soma = 0

        for i in range(0, len(dados_bits), 8):
            bloco = dados_bits[i:i+8]
            soma += int(bloco, 2)

            # Soma o carry novamente ao resultado de 8 bits.
            while soma > 255:
                soma = (soma & 255) + (soma >> 8)
                
        return soma

    def enquadramento_checksum(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")

        soma = self._soma_blocos_8bits(dados_bits)
        checksum_int = soma ^ 255
        checksum_bits = format(checksum_int, '08b')

        return dados_bits + checksum_bits

    def desenquadramento_checksum(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro):
            return None, "Erro de Transmissão"

        if len(quadro) < 9:
            return None, "Erro de Transmissão"

        soma_total = self._soma_blocos_8bits(quadro)
        
        if soma_total != 255:
            return None, "Erro de Transmissão"

        dados_originais = quadro[:-8]
        return dados_originais, None

    # CRC-32
    
    POLINOMIO_CRC32 = "100000100110000010001110110110111"

    def _divisao_crc(self, bits_dividendo: str, polinomio: str) -> str:
        dados_lista = list(bits_dividendo)

        # Executa a divisão polinomial usando somente XOR.
        for i in range(len(dados_lista) - len(polinomio) + 1):
            if dados_lista[i] == '1':
                for j in range(len(polinomio)):
                    bit_a = int(dados_lista[i + j])
                    bit_b = int(polinomio[j])
                    dados_lista[i + j] = str(bit_a ^ bit_b)

        grau = len(polinomio) - 1
        return ''.join(dados_lista[-grau:])

    def _calcula_crc(self, dados_bits: str, polinomio: str) -> str:
        grau = len(polinomio) - 1
        dados_padded = dados_bits + ('0' * grau)
        return self._divisao_crc(dados_padded, polinomio)

    def enquadramento_crc(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")

        crc = self._calcula_crc(dados_bits, self.POLINOMIO_CRC32)
        return dados_bits + crc

    def desenquadramento_crc(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro):
            return None, "Erro de Transmissão"

        grau = len(self.POLINOMIO_CRC32) - 1

        if len(quadro) <= grau:
            return None, "Erro de Transmissão"

        # Na recepção, o quadro completo é dividido diretamente pelo polinômio.
        resto = self._divisao_crc(quadro, self.POLINOMIO_CRC32)

        if '1' in resto:
            return None, "Erro de Transmissão"
            
        dados_originais = quadro[:-grau]
        return dados_originais, None
    
    # Correção de erros

    # HAMMING SIMPLES
    # O Hamming simples corrige um único bit errado.

    def enquadramento_hamming(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")

        m = len(dados_bits)
        r = 0
        
        while (2**r) < (m + r + 1):
            r += 1

        quadro = ['0'] * (m + r)
        j = 0

        for i in range(1, m + r + 1):
            if (i & (i - 1)) != 0:
                quadro[i - 1] = dados_bits[j]
                j += 1

        for i in range(r):
            pos = 2**i
            paridade = 0

            for j in range(1, m + r + 1):
                if j & pos:
                    paridade ^= int(quadro[j - 1])
                    
            quadro[pos - 1] = str(paridade)

        return ''.join(quadro)

    def desenquadramento_hamming(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro):
            return None, "Erro de Transmissão"

        if len(quadro) < 3:
            return None, "Erro de Transmissão"

        n = len(quadro)
        quadro_lista = list(quadro)
        sindrome = 0

        for i in range(1, n + 1):
            if quadro_lista[i - 1] == '1':
                sindrome ^= i

        aviso = None

        if sindrome != 0:
            # Em um Hamming simples, uma síndrome válida representa
            # a posição do único bit que deve ser corrigido.
            if sindrome > n:
                return None, "Erro de Hamming: a posição calculada está fora do quadro."

            if quadro_lista[sindrome - 1] == '1':
                quadro_lista[sindrome - 1] = '0'
            else:
                quadro_lista[sindrome - 1] = '1'

            # Confere se a correção deixou o quadro com síndrome zero.
            sindrome_apos_correcao = 0

            for i in range(1, n + 1):
                if quadro_lista[i - 1] == '1':
                    sindrome_apos_correcao ^= i

            if sindrome_apos_correcao != 0:
                return None, "Erro de Hamming: o quadro não pôde ser corrigido."

            aviso = f"Hamming corrigiu um erro no bit da posição {sindrome}."

        dados_originais = ""

        for i in range(1, n + 1):
            if (i & (i - 1)) != 0:
                dados_originais += quadro_lista[i - 1]

        return dados_originais, aviso


if __name__ == "__main__":
    enlace = CamadaEnlace()
    mensagem = "1011100011111000"

    quadro = enlace.enquadramento_crc(mensagem)
    recuperada, erro = enlace.desenquadramento_crc(quadro)

    # Simula um erro invertendo um bit do quadro.
    quadro_com_erro = list(quadro)
    quadro_com_erro[5] = '1' if quadro_com_erro[5] == '0' else '0'
    quadro_com_erro = ''.join(quadro_com_erro)

    recuperada_com_erro, erro_detectado = enlace.desenquadramento_crc(
        quadro_com_erro
    )

    print("Mensagem:          ", mensagem)
    print("Quadro CRC:         ", quadro)
    print("Recuperada:         ", recuperada)
    print("Erro normal:        ", erro)
    print("Quadro com erro:    ", quadro_com_erro)
    print("Dados com erro:     ", recuperada_com_erro)
    print("Erro detectado:     ", erro_detectado)
