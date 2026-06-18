class CamadaEnlace:
    
    # ==========================================
    # 1. ENQUADRAMENTO
    # ==========================================
    
    # Tamanho fixo (em bits) do cabeçalho de contagem. Com 16 bits conseguimos
    # contar quadros de até 65535 bits (~8192 caracteres), bem mais do que o
    # "Tamanho máximo de quadro" configurado na interface (1024).
    TAMANHO_CABECALHO_CONTAGEM = 16

    def enquadramento_contagem_caracteres(self, dados_bits: str) -> str:
        """
        Transmissor (TX): Adiciona, no início do quadro, um cabeçalho de
        tamanho FIXO (16 bits) informando quantos bits de dados vêm a seguir.

        Importante: o cabeçalho guarda esse número em BINÁRIO (não como
        dígitos decimais soltos), porque o resto do sistema trata tudo como
        uma sequência de bits ('0'/'1'). Usar um número decimal de tamanho
        variável (como na versão anterior) só funcionava por acaso para
        mensagens de exatamente 1 caractere; qualquer mensagem maior já
        quebrava o desenquadramento.
        """
        tamanho_dados = len(dados_bits)

        # Converte o tamanho para binário, preenchendo com zeros à esquerda
        # até ocupar exatamente TAMANHO_CABECALHO_CONTAGEM bits
        cabecalho = format(tamanho_dados, f'0{self.TAMANHO_CABECALHO_CONTAGEM}b')
        quadro = cabecalho + dados_bits
        return quadro

    def desenquadramento_contagem_caracteres(self, quadro: str) -> str:
        """
        Receptor (RX): Lê os primeiros 16 bits (o cabeçalho) para saber
        exatamente quantos bits de dados existem, e então extrai só essa
        quantidade — independente do tamanho da mensagem.
        """
        cabecalho = quadro[:self.TAMANHO_CABECALHO_CONTAGEM]
        tamanho_dados = int(cabecalho, 2)

        inicio_dados = self.TAMANHO_CABECALHO_CONTAGEM
        dados_originais = quadro[inicio_dados: inicio_dados + tamanho_dados]
        return dados_originais

    # ==========================================
    # 2. ENQUADRAMENTO COM FLAGS (Inserção de Bytes Real)
    # ==========================================
    
    # FLAGS de 8 bits para o método de inserção de bytes
    FLAG_BYTE = '01111110'
    ESC_BYTE = '01111101'

    def enquadramento_insercao_bytes(self, dados_bits: str) -> str:
        """
        Transmissor (TX): Coloca FLAGS de 1 byte nas pontas e 'escapa' flags acidentais.
        """
        quadro = ""
        # 1. Abre o quadro com a FLAG inicial
        quadro += self.FLAG_BYTE

        # 2. Percorre a mensagem BYTE por BYTE (pulando de 8 em 8)
        for i in range(0, len(dados_bits), 8):
            byte_atual = dados_bits[i:i+8]
            
            # Se o byte for igual à FLAG ou ao ESC, precisamos escondê-lo
            if byte_atual == self.FLAG_BYTE or byte_atual == self.ESC_BYTE:
                quadro += self.ESC_BYTE # Insere o ESC antes
            
            quadro += byte_atual # Adiciona o byte original

        # 3. Fecha o quadro com a FLAG final
        quadro += self.FLAG_BYTE
        
        return quadro

    def desenquadramento_insercao_bytes(self, quadro: str) -> str:
        """
        Receptor (RX): Remove as FLAGS e limpa os ESCs do texto binário.
        """
        # 1. Tira as FLAGS de início e fim (agora elas têm 8 caracteres de tamanho)
        miolo_do_quadro = quadro[8:-8]

        mensagem_limpa = ""
        ignorar_proximo_esc = False

        # 2. Analisa o recheio do quadro de 8 em 8 bits
        for i in range(0, len(miolo_do_quadro), 8):
            byte_atual = miolo_do_quadro[i:i+8]
            
            if ignorar_proximo_esc:
                # É um byte de dados protegido, apenas adicionamos
                mensagem_limpa += byte_atual
                ignorar_proximo_esc = False
                
            elif byte_atual == self.ESC_BYTE:
                # Achamos um byte de ESC! Ligamos a chave e pulamos para o próximo
                ignorar_proximo_esc = True
                
            else:
                # Byte normal, só adicionar
                mensagem_limpa += byte_atual

        return mensagem_limpa
    # ==========================================
    # 3. ENQUADRAMENTO COM INSERÇÃO DE BITS
    # ==========================================

    def enquadramento_insercao_bits(self, dados_bits: str) -> str:
        """
        Transmissor (TX): Coloca FLAGS de bits nas pontas e aplica o Bit Stuffing 
        (insere um '0' sempre que encontrar cinco '1's consecutivos).
        """
        FLAG_BITS = "01111110"
        quadro_final = ""
        contador_uns = 0
        
        # 1. Abre o quadro com a FLAG inicial
        quadro_final += FLAG_BITS
        
        # 2. Varre cada bit da mensagem
        for bit in dados_bits:
            # Adiciona o bit original ao quadro
            quadro_final += bit
            
            # Atualiza o nosso contador de segurança
            if bit == '1':
                contador_uns += 1
            else:
                contador_uns = 0 # Zerou a sequência
                
            # 3. O pulo do gato (Bit Stuffing)
            if contador_uns == 5:
                quadro_final += '0'  # Injeta o zero falso de segurança
                contador_uns = 0     # Zera o contador para recomeçar
                
        # 4. Fecha o quadro com a FLAG final
        quadro_final += FLAG_BITS
        
        return quadro_final
    
    def desenquadramento_insercao_bits(self, quadro: str) -> str:
        """
        Receptor (RX): Remove as FLAGS das pontas e retira o '0' falso 
        inserido após cinco '1's consecutivos (Bit Destuffing).
        """
        # 1. Tira as FLAGS de 8 bits do começo e do final
        # A FLAG "01111110" tem exatamente 8 caracteres de tamanho
        miolo_do_quadro = quadro[8:-8]
        
        mensagem_limpa = ""
        contador_uns = 0
        
        # 2. Analisa o recheio do quadro bit a bit
        for bit in miolo_do_quadro:
            if bit == '1':
                mensagem_limpa += bit
                contador_uns += 1
                
            else: # Se o bit for '0'
                if contador_uns == 5:
                    # Achamos o zero falso do Bit Stuffing!
                    # Nós IGNORAMOS ele (não adicionamos na mensagem_limpa)
                    # e apenas zeramos o contador para recomeçar.
                    contador_uns = 0
                else:
                    # É um zero normal que faz parte da mensagem do usuário
                    mensagem_limpa += bit
                    contador_uns = 0
                    
        return mensagem_limpa
    # ==========================================
    # 4. DETECÇÃO DE ERROS: PARIDADE PAR
    # ==========================================

    def enquadramento_paridade_par(self, dados_bits: str) -> str:
        """
        Transmissor (TX): Conta os bits '1'. Se a quantidade for par, 
        adiciona '0' no final. Se for ímpar, adiciona '1' no final.
        """
        # A função .count() do Python já faz o trabalho duro de contar para a gente
        contador_uns = dados_bits.count('1')
        
        # O operador % 2 pega o resto da divisão. Se for 0, é par.
        if contador_uns % 2 == 0:
            bit_paridade = '0'
        else:
            bit_paridade = '1'
            
        quadro_final = dados_bits + bit_paridade
        return quadro_final

    def desenquadramento_paridade_par(self, quadro: str) -> str:
        """
        Receptor (RX): Verifica se a quantidade total de '1's é par. 
        Se não for, acusa o erro. Depois, retira o bit de paridade.
        """
        contador_uns = quadro.count('1')
        
        if contador_uns % 2 != 0:
            print("ALERTA [RX]: Erro de paridade detectado! O quadro foi corrompido no canal.")
            # Num simulador real, o pacote seria descartado e pediria retransmissão aqui.
            
        # O dado original é o quadro inteiro, tirando apenas o último caractere ([:-1])
        dados_originais = quadro[:-1]
        
        return dados_originais
    # ==========================================
    # 5. DETECÇÃO DE ERROS: CHECKSUM
    # ==========================================

    def _soma_blocos_8bits(self, dados_bits: str) -> int:
        """
        Função auxiliar matemática: Divide os bits em blocos de 8, 
        soma todos e trata o 'estouro' (carry).
        """
        # Se a mensagem não for múltipla de 8, preenchemos com zeros à esquerda
        resto = len(dados_bits) % 8
        if resto != 0:
            dados_bits = dados_bits.zfill(len(dados_bits) + (8 - resto))

        soma = 0
        # Pula de 8 em 8 pegando os blocos
        for i in range(0, len(dados_bits), 8):
            bloco = dados_bits[i:i+8]
            # Converte a string binária para número inteiro e soma
            soma += int(bloco, 2)

            # Se a soma passar de 8 bits (255), pegamos o que sobrou e somamos de volta
            if soma > 255:
                soma = (soma & 255) + 1
                
        return soma

    def enquadramento_checksum(self, dados_bits: str) -> str:
        """
        Transmissor (TX): Calcula a soma, inverte os bits e anexa no final.
        """
        soma = self._soma_blocos_8bits(dados_bits)
        
        # Inverte os bits (Complemento de 1). 
        # Em Python, fazer a operação XOR (^) com 255 (que é 11111111) inverte os zeros e uns.
        checksum_int = soma ^ 255
        
        # Converte o resultado de volta para uma string binária de 8 letras
        checksum_bits = format(checksum_int, '08b')
        
        # O quadro final é a mensagem original + a assinatura de 8 bits no final
        return dados_bits + checksum_bits

    def desenquadramento_checksum(self, quadro: str) -> str:
        """
        Receptor (RX): Soma tudo (dados + checksum recebido). 
        Se o resultado não for uma sequência só de uns (255), houve erro.
        """
        # Faz a soma de todo o pacote que chegou
        soma_total = self._soma_blocos_8bits(quadro)
        
        # A regra matemática diz que uma transmissão perfeita resulta em 255 (11111111)
        if soma_total != 255:
            print(" ALERTA [RX]: Erro de Checksum detectado! O quadro foi corrompido no canal.")
            
        # Retira os últimos 8 bits (o checksum) para devolver apenas a mensagem limpa
        dados_originais = quadro[:-8]
        
        return dados_originais
    # ==========================================
    # 6. DETECÇÃO DE ERROS: CRC-32 (IEEE 802)
    # ==========================================
    
    # Este é o polinômio gerador oficial do padrão IEEE 802 (Ethernet/Wi-Fi)
    POLINOMIO_CRC32 = "100000100110000010001110110110111"

    def _calcula_crc(self, dados_bits: str, polinomio: str) -> str:
        """
        Função auxiliar matemática: Faz a divisão polinomial módulo-2 (XOR) 
        e retorna o 'resto' da divisão.
        """
        # O grau é o tamanho do polinômio menos 1 (no caso do CRC-32, é 32)
        grau = len(polinomio) - 1
        
        # O TX adiciona 'zeros' no final da mensagem equivalentes ao grau
        dados_padded = dados_bits + ('0' * grau)
        
        # Convertendo para uma lista para podermos alterar os bits individualmente
        dados_lista = list(dados_padded)
        
        # A divisão longa em si
        for i in range(len(dados_bits)):
            # Se o bit atual for '1', o divisor "cabe" aqui, então fazemos o XOR
            if dados_lista[i] == '1':
                for j in range(len(polinomio)):
                    # Operação XOR: int(a) ^ int(b)
                    bit_a = int(dados_lista[i+j])
                    bit_b = int(polinomio[j])
                    dados_lista[i+j] = str(bit_a ^ bit_b)
                    
        # O resto da divisão são exatamente os últimos bits do tamanho do grau
        resto = ''.join(dados_lista[-grau:])
        return resto

    def enquadramento_crc(self, dados_bits: str) -> str:
        """
        Transmissor (TX): Calcula o CRC de 32 bits e anexa no final da mensagem.
        """
        crc = self._calcula_crc(dados_bits, self.POLINOMIO_CRC32)
        
        # O quadro final = Mensagem Original + Assinatura CRC de 32 bits
        return dados_bits + crc

    def desenquadramento_crc(self, quadro: str) -> str:
        """
        Receptor (RX): Divide o quadro inteiro pelo polinômio. 
        Se o resto não for totalmente zero, o quadro tem erro.
        """
        # Faz a divisão do quadro completo que chegou do canal
        resto = self._calcula_crc(quadro, self.POLINOMIO_CRC32)
        
        # Se existir qualquer '1' no resto da divisão, a conta não bateu
        if '1' in resto:
            print("ALERTA [RX]: Erro de CRC detectado! Ruído no canal de comunicação.")
            
        # O RX arranca os 32 bits do CRC fora e devolve a mensagem pura
        dados_originais = quadro[:-32]
        
        return dados_originais
    # ==========================================
    # 7. CORREÇÃO DE ERROS: CÓDIGO DE HAMMING
    # ==========================================

    def enquadramento_hamming(self, dados_bits: str) -> str:
        """
        Transmissor (TX): Calcula os bits redundantes, posiciona nas potências de 2
        e gera os valores de paridade par.
        """
        m = len(dados_bits)
        r = 0
        
        # 1. Descobre quantos bits de paridade (r) precisamos
        while (2**r) < (m + r + 1):
            r += 1

        # Cria uma lista vazia com o tamanho total (dados + paridades)
        quadro = ['0'] * (m + r)
        
        # 2. Posiciona os bits de DADOS nos espaços que NÃO são potências de 2
        j = 0
        for i in range(1, m + r + 1):
            # O truque (i & (i - 1)) != 0 verifica se 'i' NÃO é potência de 2
            if (i & (i - 1)) != 0:
                quadro[i-1] = dados_bits[j]
                j += 1

        # 3. Calcula o valor de cada bit de PARIDADE
        for i in range(r):
            pos = 2**i
            paridade = 0
            for j in range(1, m + r + 1):
                # Se a posição j faz parte do grupo deste bit de paridade (bitwise AND)
                if j & pos:
                    paridade ^= int(quadro[j-1])
                    
            quadro[pos-1] = str(paridade)

        return ''.join(quadro)

    def desenquadramento_hamming(self, quadro: str) -> str:
        """
        Receptor (RX): Calcula a síndrome. Se houver erro, descobre a posição exata,
        corrige o bit e extrai apenas a mensagem original.
        """
        n = len(quadro)
        quadro_lista = list(quadro)
        sindrome = 0

        # 1. Calcula a Síndrome (faz um XOR com a posição 1-based de todos os bits '1')
        for i in range(1, n + 1):
            if quadro_lista[i-1] == '1':
                sindrome ^= i

        # 2. A Autocorreção Mágica
        if sindrome != 0:
            print(f"ALERTA [RX]: Ruído corrompeu a posição {sindrome}!")
            print("[RX]: O Hamming está corrigindo o bit automaticamente...")
            
            # Se era 1 vira 0, se era 0 vira 1
            if quadro_lista[sindrome-1] == '1':
                quadro_lista[sindrome-1] = '0'
            else:
                quadro_lista[sindrome-1] = '1'

        # 3. Extrai apenas os bits de DADOS (ignora os que estão nas potências de 2)
        dados_originais = ""
        for i in range(1, n + 1):
            if (i & (i - 1)) != 0:
                dados_originais += quadro_lista[i-1]

        return dados_originais
# ==========================================
# ÁREA DE TESTES NO TERMINAL
# ==========================================
if __name__ == "__main__":
    enlace = CamadaEnlace()
    
    # Nossa mensagem de 4 bits (Clássico Hamming 7,4)
    mensagem_bits = "1011"
    print(f"Mensagem original:  {mensagem_bits}")
    print("-" * 65)
    
    # 1. TX posiciona e calcula as paridades
    quadro_enviado = enlace.enquadramento_hamming(mensagem_bits)
    print(f"[TX] Quadro Hamming: {quadro_enviado}")
    
    print("\n--- TESTE 1: Transmissão Perfeita ---")
    mensagem_extraida = enlace.desenquadramento_hamming(quadro_enviado)
    print(f"[RX] Mens. extraída: {mensagem_extraida}")
    
    print("\n--- TESTE 2: Sofrendo Ruído (Invertendo o 6º bit) ---")
    # Forçando um erro no meio do caminho (posição 6, índice 5)
    quadro_lista = list(quadro_enviado)
    quadro_lista[5] = '0' if quadro_lista[5] == '1' else '1'
    quadro_corrompido = "".join(quadro_lista)
    
    print(f"[Canal] O quadro chegou quebrado: {quadro_corrompido}")
    
    # O RX vai receber o quadro quebrado, achar a posição, consertar e devolver a mensagem certa!
    mensagem_extraida_com_erro = enlace.desenquadramento_hamming(quadro_corrompido)
    print(f"[RX] Mensagem SALVA: {mensagem_extraida_com_erro}")