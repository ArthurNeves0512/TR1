class CamadaEnlace:

    # ENQUADRAMENTO 

    def __init__(self, config=None):
        self.config = config
        self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM = 1


    def enquadramento_contagem_caracteres(self, dados_bits: str) -> str:
        # Cada 8 bits = 1 byte de carga útil
        bytes_dados = len(dados_bits) // 8
        # O cabeçalho conta a si mesmo, então soma 1
        valor_cabecalho = bytes_dados + 1
        cabecalho = format(valor_cabecalho, '08b')
        return cabecalho + dados_bits

    def desenquadramento_contagem_caracteres(self, quadro: str) -> tuple:
        # Valida tamanho mínimo
        if len(quadro) < 8:
            return (None, "Erro no quadro: cabeçalho incompleto.")

        # Valida que só há '0' e '1'
        if not all(b in '01' for b in quadro):
            return (None, "Erro no quadro: entrada contém caracteres inválidos.")

        cabecalho_bits = quadro[:8]
        valor_cabecalho = int(cabecalho_bits, 2)

        # Valor 0 ou 1 é inválido (mínimo é 1 byte de cabeçalho + algum dado = 2)
        if valor_cabecalho < 1:
            return (None, "Erro no quadro: valor de cabeçalho inválido.")

        # Subtrai 1 para obter a quantidade de bytes de carga útil
        bytes_dados = valor_cabecalho - 1
        bits_dados = bytes_dados * 8

        dados = quadro[8: 8 + bits_dados]

        # Verifica se a carga útil tem o tamanho prometido pelo cabeçalho
        if len(dados) < bits_dados:
            return (None, "Erro no quadro: carga útil menor que o informado no cabeçalho.")

        return (dados, None)

    # Inserção de bytes

    FLAG_BYTE = '01111110'
    ESC_BYTE  = '01111101'

    def enquadramento_insercao_bytes(self, dados_bits: str) -> str:
        quadro = self.FLAG_BYTE

        for i in range(0, len(dados_bits), 8):
            byte_atual = dados_bits[i:i+8]
            # Protege FLAG e ESC com um ESC antes
            if byte_atual == self.FLAG_BYTE or byte_atual == self.ESC_BYTE:
                quadro += self.ESC_BYTE
            quadro += byte_atual

        quadro += self.FLAG_BYTE
        return quadro

    def desenquadramento_insercao_bytes(self, quadro: str) -> tuple:
        # Valida tamanho mínimo (FLAG + FLAG = 16 bits)
        if len(quadro) < 16:
            return (None, "Erro no quadro: quadro muito curto.")

        # Valida FLAGS externas
        if quadro[:8] != self.FLAG_BYTE:
            return (None, "Erro no quadro: FLAG inicial ausente ou alterada.")
        if quadro[-8:] != self.FLAG_BYTE:
            return (None, "Erro no quadro: FLAG final ausente ou alterada.")

        miolo = quadro[8:-8]

        # Valida que o miolo é múltiplo de 8 bits
        if len(miolo) % 8 != 0:
            return (None, "Erro no quadro: byte incompleto no conteúdo.")

        mensagem = ""
        i = 0
        while i < len(miolo):
            byte_atual = miolo[i:i+8]

            if byte_atual == self.ESC_BYTE:
                # Deve existir um byte seguinte
                if i + 8 >= len(miolo):
                    return (None, "Erro no quadro: ESC sem byte seguinte.")
                byte_seguinte = miolo[i+8:i+16]
                # O byte seguinte ao ESC só pode ser FLAG ou ESC
                if byte_seguinte != self.FLAG_BYTE and byte_seguinte != self.ESC_BYTE:
                    return (None, "Erro no quadro: ESC seguido de byte inválido.")
                mensagem += byte_seguinte
                i += 16
            else:
                mensagem += byte_atual
                i += 8

        return (mensagem, None)

    # Inserção de bits

    FLAG_BITS = '01111110'

    def enquadramento_insercao_bits(self, dados_bits: str) -> str:
        quadro = self.FLAG_BITS
        contador_uns = 0

        for bit in dados_bits:
            quadro += bit
            if bit == '1':
                contador_uns += 1
            else:
                contador_uns = 0
            # Após 5 uns consecutivos, insere um zero de stuffing
            if contador_uns == 5:
                quadro += '0'
                contador_uns = 0

        quadro += self.FLAG_BITS
        return quadro

    def desenquadramento_insercao_bits(self, quadro: str) -> tuple:
        # Valida FLAGS externas
        if len(quadro) < 16:
            return (None, "Erro no quadro: quadro muito curto.")
        if quadro[:8] != self.FLAG_BITS:
            return (None, "Erro no quadro: FLAG inicial ausente ou alterada.")
        if quadro[-8:] != self.FLAG_BITS:
            return (None, "Erro no quadro: FLAG final ausente ou alterada.")

        miolo = quadro[8:-8]
        mensagem = ""
        contador_uns = 0
        i = 0

        while i < len(miolo):
            bit = miolo[i]
            if bit == '1':
                mensagem += bit
                contador_uns += 1
                # Após 5 uns, o próximo deve ser o zero
                if contador_uns == 5:
                    i += 1
                    if i >= len(miolo):
                        return (None, "Erro no quadro: zero de stuffing ausente após cinco bits 1.")
                    proximo = miolo[i]
                    if proximo != '0':
                        return (None, "Erro no quadro: esperado zero de stuffing, encontrado 1.")
                    # Descarta o zero inserido e reinicia contagem
                    contador_uns = 0
            else:
                mensagem += bit
                contador_uns = 0
            i += 1

        return (mensagem, None)

    # Paridade par

    def enquadramento_paridade_par(self, dados_bits: str) -> str:
        contador_uns = dados_bits.count('1')
        # Garante que o total de números 1 no quadro seja par
        bit_paridade = '1' if contador_uns % 2 != 0 else '0'
        return dados_bits + bit_paridade

    def desenquadramento_paridade_par(self, quadro: str) -> tuple:
        contador_uns = quadro.count('1')
        if contador_uns % 2 != 0:
            return (None, "Erro no quadro: erro de paridade par detectado.")
        # Remove o bit de paridade e retorna a carga útil
        return (quadro[:-1], None)

    # Checksum 

    def _soma_blocos_8bits(self, dados_bits: str) -> int:
        # Garante múltiplo de 8 preenchendo à esquerda com zeros
        resto = len(dados_bits) % 8
        if resto != 0:
            dados_bits = dados_bits.zfill(len(dados_bits) + (8 - resto))

        soma = 0
        for i in range(0, len(dados_bits), 8):
            bloco = dados_bits[i:i+8]
            soma += int(bloco, 2)
            # Retorna o carry para o bit menos significativo
            while soma > 255:
                soma = (soma & 0xFF) + (soma >> 8)

        return soma

    def enquadramento_checksum(self, dados_bits: str) -> str:
        soma = self._soma_blocos_8bits(dados_bits)
        checksum_int = soma ^ 0xFF          # Complemento de um
        checksum_bits = format(checksum_int, '08b')
        return dados_bits + checksum_bits

    def desenquadramento_checksum(self, quadro: str) -> tuple:
        soma_total = self._soma_blocos_8bits(quadro)
        if soma_total != 255:
            return (None, "Erro no quadro: erro de checksum detectado.")
        return (quadro[:-8], None)

    # CRC-32

    POLINOMIO_CRC32 = "100000100110000010001110110110111"

    def _calcula_crc(self, dados_bits: str, polinomio: str) -> str:
        grau = len(polinomio) - 1
        # Acrescenta zeros equivalentes ao grau do polinômio
        dados_lista = list(dados_bits + '0' * grau)

        for i in range(len(dados_bits)):
            if dados_lista[i] == '1':
                for j in range(len(polinomio)):
                    dados_lista[i+j] = str(int(dados_lista[i+j]) ^ int(polinomio[j]))

        resto = ''.join(dados_lista[-grau:])
        return resto

    def enquadramento_crc(self, dados_bits: str) -> str:
        crc = self._calcula_crc(dados_bits, self.POLINOMIO_CRC32)
        return dados_bits + crc

    def desenquadramento_crc(self, quadro: str) -> tuple:
        # Divide o quadro completo (dados + CRC) pelo polinômio; resto deve ser zero
        resto = self._calcula_crc(quadro, self.POLINOMIO_CRC32)
        if '1' in resto:
            return (None, "Erro no quadro: erro de CRC-32 detectado.")
        return (quadro[:-32], None)

    # Hamming

    def enquadramento_hamming(self, dados_bits: str) -> str:
        m = len(dados_bits)
        # Calcula o número mínimo de bits de paridade necessários
        r = 0
        while (2 ** r) < (m + r + 1):
            r += 1

        # Monta o quadro reservando posições de potências de 2 para paridade
        quadro = ['0'] * (m + r)
        j = 0
        for i in range(1, m + r + 1):
            if (i & (i - 1)) != 0:          # Não é potência de 2 → bit de dados
                quadro[i-1] = dados_bits[j]
                j += 1

        # Calcula cada bit de paridade (paridade par)
        for i in range(r):
            pos = 2 ** i
            paridade = 0
            for k in range(1, m + r + 1):
                if k & pos:
                    paridade ^= int(quadro[k-1])
            quadro[pos-1] = str(paridade)

        return ''.join(quadro)

    def desenquadramento_hamming(self, quadro: str) -> tuple:
        n = len(quadro)
        quadro_lista = list(quadro)

        # Calcula a síndrome recalculando todas as paridades
        sindrome = 0
        for i in range(1, n + 1):
            if quadro_lista[i-1] == '1':
                sindrome ^= i

        mensagem_correcao = None

        if sindrome != 0:
            # Valida que a síndrome aponta para uma posição existente
            if sindrome > n:
                return (None, "Erro no quadro: síndrome Hamming inválida.")
            # Corrige o bit errado
            quadro_lista[sindrome-1] = '0' if quadro_lista[sindrome-1] == '1' else '1'
            mensagem_correcao = f"Hamming detectou e corrigiu o bit da posição {sindrome}."

        # Remove os bits de paridade e recupera apenas os dados
        dados_originais = ""
        for i in range(1, n + 1):
            if (i & (i - 1)) != 0:          # Não é potência de 2 → bit de dados
                dados_originais += quadro_lista[i-1]

        return (dados_originais, mensagem_correcao)



