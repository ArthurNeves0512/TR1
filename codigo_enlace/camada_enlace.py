class CamadaEnlace:

    def __init__(self, config=None):
        self.config = config or {}
        self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM = 1
        self.ultimos_quadros = []

    def _validar_bits(self, bits: str) -> bool:
        return isinstance(bits, str) and bits != "" and all(bit in "01" for bit in bits)

    def _tamanho_maximo_quadro(self) -> int:
        try:
            tamanho = int(self.config.get("frame_size", 4))
        except (TypeError, ValueError) as erro:
            raise ValueError("O tamanho máximo do quadro deve ser um número inteiro.") from erro

        if tamanho <= 0:
            raise ValueError("O tamanho máximo do quadro deve ser maior que zero.")
        return tamanho

    # ENQUADRAMENTO POR CONTAGEM DE CARACTERES

    def enquadramento_contagem_caracteres(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")
        if len(dados_bits) % 8 != 0:
            raise ValueError("A contagem de caracteres exige uma quantidade inteira de bytes.")

        tamanho_maximo = self._tamanho_maximo_quadro()
        if tamanho_maximo < 2:
            raise ValueError(
                "Na contagem de caracteres, o quadro deve ter pelo menos 2 bytes: "
                "1 de cabeçalho e 1 de dados."
            )
        if tamanho_maximo > 255:
            raise ValueError(
                "O cabeçalho de 8 bits permite no máximo 255 bytes por quadro."
            )

        bytes_dados = [dados_bits[i:i + 8] for i in range(0, len(dados_bits), 8)]
        capacidade_dados = tamanho_maximo - self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM
        quadros = []

        for inicio in range(0, len(bytes_dados), capacidade_dados):
            carga = bytes_dados[inicio:inicio + capacidade_dados]
            total_bytes = self.TAMANHO_EM_BYTES_CABECALHO_CONTAGEM + len(carga)
            cabecalho = format(total_bytes, "08b")
            quadros.append(cabecalho + "".join(carga))

        self.ultimos_quadros = quadros
        return "".join(quadros)

    def desenquadramento_contagem_caracteres(self, fluxo: str) -> tuple:
        if not self._validar_bits(fluxo):
            return None, "Fluxo inválido: eram esperados apenas bits 0 e 1."
        if len(fluxo) % 8 != 0:
            return None, "Fluxo de contagem incompleto: o tamanho não é múltiplo de 8 bits."

        tamanho_maximo = self._tamanho_maximo_quadro()
        posicao = 0
        cargas = []
        quadros = []

        while posicao < len(fluxo):
            if len(fluxo) - posicao < 8:
                return None, "Cabeçalho de contagem incompleto."

            total_bytes = int(fluxo[posicao:posicao + 8], 2)
            if total_bytes < 2:
                return None, "Cabeçalho de contagem inválido."
            if total_bytes > tamanho_maximo:
                return None, "O cabeçalho informa um quadro maior que o tamanho configurado."

            tamanho_bits = total_bytes * 8
            fim = posicao + tamanho_bits
            if fim > len(fluxo):
                return None, "Quadro truncado: faltam bits indicados pelo cabeçalho."

            quadro_atual = fluxo[posicao:fim]
            quadros.append(quadro_atual)
            cargas.append(quadro_atual[8:])
            posicao = fim

        self.ultimos_quadros = quadros
        return "".join(cargas), None


    # ENQUADRAMENTO INSERÇÃO DE BYTES
    FLAG_BYTE = "01111110"
    ESC_BYTE = "01111101"
    
    def enquadramento_insercao_bytes(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")
        if len(dados_bits) % 8 != 0:
            raise ValueError("A inserção de bytes exige uma quantidade inteira de bytes.")

        tamanho_maximo = self._tamanho_maximo_quadro()
        if tamanho_maximo < 3:
            raise ValueError(
                "A inserção de bytes exige pelo menos 3 bytes por quadro: "
                "FLAG inicial, um byte de dados e FLAG final."
            )

        bytes_dados = [dados_bits[i:i + 8] for i in range(0, len(dados_bits), 8)]
        quadros = []
        carga_codificada = []
        tamanho_atual = 2  

        def fechar_quadro():
            if carga_codificada:
                quadros.append(self.FLAG_BYTE + "".join(carga_codificada) + self.FLAG_BYTE)

        for byte_atual in bytes_dados:
            if byte_atual in (self.FLAG_BYTE, self.ESC_BYTE):
                bytes_codificados = [self.ESC_BYTE, byte_atual]
            else:
                bytes_codificados = [byte_atual]

            custo = len(bytes_codificados)
            if carga_codificada and tamanho_atual + custo > tamanho_maximo:
                fechar_quadro()
                carga_codificada = []
                tamanho_atual = 2

            if tamanho_atual + custo > tamanho_maximo:
                raise ValueError(
                    "O tamanho configurado é pequeno demais para transportar um byte escapado. "
                    "Use pelo menos 4 bytes por quadro."
                )

            carga_codificada.extend(bytes_codificados)
            tamanho_atual += custo

        fechar_quadro()
        self.ultimos_quadros = quadros
        return "".join(quadros)

    def desenquadramento_insercao_bytes(self, fluxo: str) -> tuple:
        if not self._validar_bits(fluxo):
            return None, "Fluxo inválido: eram esperados apenas bits 0 e 1."
        if len(fluxo) % 8 != 0:
            return None, "Fluxo de inserção de bytes incompleto."

        bytes_fluxo = [fluxo[i:i + 8] for i in range(0, len(fluxo), 8)]
        tamanho_maximo = self._tamanho_maximo_quadro()
        posicao = 0
        cargas = []
        quadros = []

        while posicao < len(bytes_fluxo):
            if bytes_fluxo[posicao] != self.FLAG_BYTE:
                return None, "FLAG inicial ausente ou corrompida."

            inicio_quadro = posicao
            posicao += 1
            carga = []
            encontrou_fim = False

            while posicao < len(bytes_fluxo):
                byte_atual = bytes_fluxo[posicao]

                if byte_atual == self.FLAG_BYTE:
                    encontrou_fim = True
                    fim_quadro = posicao
                    posicao += 1
                    break

                if byte_atual == self.ESC_BYTE:
                    posicao += 1
                    if posicao >= len(bytes_fluxo):
                        return None, "Byte ESC sem byte posterior."

                    byte_escapado = bytes_fluxo[posicao]
                    if byte_escapado not in (self.FLAG_BYTE, self.ESC_BYTE):
                        return None, "Sequência de escape inválida."
                    carga.append(byte_escapado)
                    posicao += 1
                    continue

                carga.append(byte_atual)
                posicao += 1

            if not encontrou_fim:
                return None, "FLAG final ausente ou corrompida."

            quantidade_bytes_quadro = fim_quadro - inicio_quadro + 1
            if quantidade_bytes_quadro > tamanho_maximo:
                return None, "Foi recebido um quadro maior que o tamanho configurado."
            if not carga:
                return None, "Foi recebido um quadro sem carga útil."

            quadros.append("".join(bytes_fluxo[inicio_quadro:fim_quadro + 1]))
            cargas.append("".join(carga))

        self.ultimos_quadros = quadros
        return "".join(cargas), None

    # ENQUADRAMENTO iNSERÇÃO DE BITS

    def enquadramento_insercao_bits(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")

        tamanho_maximo_bits = self._tamanho_maximo_quadro() * 8
        if tamanho_maximo_bits < 17:
            raise ValueError(
                "A inserção de bits precisa de espaço para duas FLAGS e ao menos um bit de dados."
            )

        quadros = []
        indice = 0

        while indice < len(dados_bits):
            carga_codificada = ""
            contador_uns = 0

            while indice < len(dados_bits):
                bit = dados_bits[indice]

                if bit == "0":
                    trecho = "0"
                    novo_contador = 0
                elif contador_uns == 4:
                    trecho = "10"
                    novo_contador = 0
                else:
                    trecho = "1"
                    novo_contador = contador_uns + 1

                tamanho_completo = 8 + len(carga_codificada) + len(trecho) + 8
                if tamanho_completo > tamanho_maximo_bits:
                    break

                carga_codificada += trecho
                contador_uns = novo_contador
                indice += 1

            if carga_codificada == "":
                raise ValueError("O tamanho configurado é pequeno demais para formar um quadro.")

            quadros.append(self.FLAG_BYTE + carga_codificada + self.FLAG_BYTE)

        self.ultimos_quadros = quadros
        return "".join(quadros)

    def desenquadramento_insercao_bits(self, fluxo: str) -> tuple:
        if not self._validar_bits(fluxo):
            return None, "Fluxo inválido: eram esperados apenas bits 0 e 1."
        if not fluxo.startswith(self.FLAG_BYTE) or not fluxo.endswith(self.FLAG_BYTE):
            return None, "FLAG inicial ou final ausente."

        partes = fluxo.split(self.FLAG_BYTE)
        if partes[0] != "" or partes[-1] != "":
            return None, "Existem bits fora das FLAGS."

        cargas_codificadas = [parte for parte in partes[1:-1] if parte != ""]
        if not cargas_codificadas:
            return None, "Nenhum quadro válido foi encontrado."

        tamanho_maximo_bits = self._tamanho_maximo_quadro() * 8
        cargas = []
        quadros = []

        for carga_codificada in cargas_codificadas:
            if len(carga_codificada) + 16 > tamanho_maximo_bits:
                return None, "Foi recebido um quadro maior que o tamanho configurado."

            mensagem_limpa = ""
            contador_uns = 0
            i = 0

            while i < len(carga_codificada):
                bit = carga_codificada[i]

                if bit == "1":
                    mensagem_limpa += "1"
                    contador_uns += 1

                    if contador_uns == 5:
                        if i + 1 >= len(carga_codificada):
                            return None, "Inserção de bits incompleta após cinco bits 1."
                        if carga_codificada[i + 1] != "0":
                            return None, "Foi encontrada uma sequência de bits inválida."
                        i += 1
                        contador_uns = 0
                else:
                    mensagem_limpa += "0"
                    contador_uns = 0

                i += 1

            quadros.append(self.FLAG_BYTE + carga_codificada + self.FLAG_BYTE)
            cargas.append(mensagem_limpa)

        self.ultimos_quadros = quadros
        return "".join(cargas), None

    # BIT DE PARIDADE PAR

    def enquadramento_paridade_par(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")

        bit_paridade = "0" if dados_bits.count("1") % 2 == 0 else "1"
        return dados_bits + bit_paridade

    def desenquadramento_paridade_par(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro) or len(quadro) < 2:
            return None, "Quadro de paridade inválido."
        if quadro.count("1") % 2 != 0:
            return None, "A paridade par detectou erro na transmissão."
        return quadro[:-1], None

    # CHECKSUM 

    def _soma_blocos_8bits(self, dados_bits: str) -> int:
        resto = len(dados_bits) % 8
        if resto != 0:
            dados_bits = dados_bits.zfill(len(dados_bits) + (8 - resto))

        soma = 0
        for i in range(0, len(dados_bits), 8):
            soma += int(dados_bits[i:i + 8], 2)
            while soma > 255:
                soma = (soma & 255) + (soma >> 8)
        return soma

    def enquadramento_checksum(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")

        soma = self._soma_blocos_8bits(dados_bits)
        checksum_bits = format(soma ^ 255, "08b")
        return dados_bits + checksum_bits

    def desenquadramento_checksum(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro) or len(quadro) < 9:
            return None, "Quadro de checksum inválido."

        if self._soma_blocos_8bits(quadro) != 255:
            return None, "O checksum detectou erro na transmissão."
        return quadro[:-8], None
    
    # CRC-32 

    POLINOMIO_CRC32 = "100000100110000010001110110110111"

    def _divisao_crc(self, bits_dividendo: str, polinomio: str) -> str:
        dados_lista = list(bits_dividendo)

        for i in range(len(dados_lista) - len(polinomio) + 1):
            if dados_lista[i] == "1":
                for j in range(len(polinomio)):
                    dados_lista[i + j] = str(
                        int(dados_lista[i + j]) ^ int(polinomio[j])
                    )

        grau = len(polinomio) - 1
        return "".join(dados_lista[-grau:])

    def _calcula_crc(self, dados_bits: str, polinomio: str) -> str:
        grau = len(polinomio) - 1
        return self._divisao_crc(dados_bits + ("0" * grau), polinomio)

    def enquadramento_crc(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")
        return dados_bits + self._calcula_crc(dados_bits, self.POLINOMIO_CRC32)

    def desenquadramento_crc(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro):
            return None, "Quadro CRC inválido."

        grau = len(self.POLINOMIO_CRC32) - 1
        if len(quadro) <= grau:
            return None, "Quadro CRC incompleto."

        resto = self._divisao_crc(quadro, self.POLINOMIO_CRC32)
        if "1" in resto:
            return None, "O CRC-32 detectou erro na transmissão."
        return quadro[:-grau], None

    # HAMMING 

    def _codificar_hamming_8bits(self, dados_8bits: str) -> str:
        quadro = ["0"] * 12
        indice_dado = 0

        for posicao in range(1, 13):
            if (posicao & (posicao - 1)) != 0:
                quadro[posicao - 1] = dados_8bits[indice_dado]
                indice_dado += 1

        for posicao_paridade in (1, 2, 4, 8):
            paridade = 0
            for posicao in range(1, 13):
                if posicao & posicao_paridade:
                    paridade ^= int(quadro[posicao - 1])
            quadro[posicao_paridade - 1] = str(paridade)

        return "".join(quadro)

    def enquadramento_hamming(self, dados_bits: str) -> str:
        if not self._validar_bits(dados_bits):
            raise ValueError("Os dados devem conter somente bits 0 e 1.")
        if len(dados_bits) % 8 != 0:
            raise ValueError("O Hamming exige dados em blocos completos de 8 bits.")

        return "".join(
            self._codificar_hamming_8bits(dados_bits[i:i + 8])
            for i in range(0, len(dados_bits), 8)
        )

    def desenquadramento_hamming(self, quadro: str) -> tuple:
        if not self._validar_bits(quadro):
            return None, "Quadro Hamming inválido."
        if len(quadro) % 12 != 0:
            return None, "Quadro Hamming incompleto"

        dados_recuperados = []
        posicoes_corrigidas = []

        for inicio in range(0, len(quadro), 12):
            bloco = list(quadro[inicio:inicio + 12])
            sindrome = 0

            for posicao in range(1, 13):
                if bloco[posicao - 1] == "1":
                    sindrome ^= posicao

            if sindrome != 0:
                if sindrome > 12:
                    return None, (
                        "O Hamming calculou uma posição fora do bloco. "
                        "Pode ter ocorrido mais de um erro no mesmo bloco."
                    )

                bloco[sindrome - 1] = "0" if bloco[sindrome - 1] == "1" else "1"
                posicoes_corrigidas.append(inicio + sindrome)

            for posicao in range(1, 13):
                if (posicao & (posicao - 1)) != 0:
                    dados_recuperados.append(bloco[posicao - 1])

        aviso = None
        if len(posicoes_corrigidas) == 1:
            aviso = f"Hamming corrigiu o bit da posição {posicoes_corrigidas[0]}."
        elif len(posicoes_corrigidas) > 1:
            lista = ", ".join(str(posicao) for posicao in posicoes_corrigidas)
            aviso = f"Hamming corrigiu os bits das posições {lista}."

        return "".join(dados_recuperados), aviso
