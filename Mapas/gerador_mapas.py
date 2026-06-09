import random 
class GeradorProcedural:
    def __init__(self, linhas=17, colunas=24):
        self.linhas = linhas
        self.colunas = colunas

    def gerar_fase(self):
        #serve para gerar uma matriz de mapa em regras inteligentes 
        # o mapa é preechido totalmente pelo chão=0

        mapa = [[0 for _ in range(self.colunas)] for _ in range(self.linhas)]

        #cria as bordas indestrutiveis do mapa
        for l in range (self.linhas):
            for c in range(self.colunas):
                if l == 0 or l == self.linhas-1 or c == 0 or c == self.colunas-1:
                    mapa[l][c] = 1
        
        #cria piláres fixos e intercalados
        for l in range(2, self.linhas-2, 2):
            for c in range(2, self.colunas-2, 2):
                mapa[l][c] = 1

        #cria a "zona segura" do jogador no canto superior esquerdo.
        zona_seguras = [(1,1), (1,2), (2,1), (2,1), (1,3), (3,1)]

        #destribui os blocos detruíveis
        for l in range(1, self.linhas-1):
            for c in range(1, self.colunas-1):
                if mapa[l][c] == 0 and (l,c) not in zona_seguras:
                    if random.random() < 0.35: #35% de chance de criar um bloco detruível
                        mapa[l][c] = 2

        #os blocos de minérios destrutiveis
        num_veios = random.randint(2, 6) #número de veios de minério
        for _ in range(num_veios):
            #local aleatório e distante do spawn do mike
            lin_veio = random.randint(3, self.linhas -2)
            col_veio = random.randint(5, self.colunas -3)

            #espalha o miério ao redor desseeeeee ponto
            tamanho_veio = random.randint(2, 4)
            for _ in range(tamanho_veio):
                if 0 <= lin_veio < self.linhas and 0 <= col_veio < self.colunas:
                    #só subistitui se for chao ou bloco que explode 
                    if mapa[lin_veio][col_veio] in [0,2]:
                        mapa[lin_veio][col_veio] = 4 # minério

                lin_veio += random.choice([-1, 0, 1]) #move o ponto do veio para criar um formato mais orgânico
                col_veio += random.choice([-1, 0, 1])

        #posiciona a saída do mapa
        saida_definida = False
        for l in range(self.linhas-2, 0, -1):
            if mapa[l][self.colunas-2] != 1:
                mapa[l][self.colunas-2] = 3 #a saida boy
                saida_definida = True 
                break 
    
        #caso de SEGURANÇAAAAAAA caso a saida seja fechada pelos blocos 
        if not saida_definida:
            mapa[self.linhas // 2][self.colunas-2] = 3

        #validação por Flood Fill / BFS (Garante que a fase tem solução)
        #se o caminho do Mike (1,1) até a saída (3) estiver totalmente bloqueado, gera outro mapa do zero

        if not self.validar_caminho(mapa):
            return self.gerar_fase()
        
        return mapa
    def validar_caminho(self,mapa):
        #testa se o jogador consegue chegar na saida

        linhas = len(mapa)
        colunas = len(mapa[0])
        visitados = [[False for _ in range(colunas)] for _ in range(linhas)]

        #fila de busca pose do mike (1,1)
        fila = [(1, 1)]
        visitados[1][1] = True
        
        while fila:
            l, c = fila.pop(0)

            # se a buscar alcançou a saida, o layout é válido
            if mapa[l][c] == 3:
                return True

            #checar os 4 lados
            for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:   
                nl = l + dl
                nc = c + dc

                if 0 <= nl < linhas and 0 <= nc < colunas:
                    ## o algoritmo pode atravessa tudos, menos as paredes fixas
                    if not visitados[nl][nc] and mapa[nl][nc] != 1:
                        visitados[nl][nc] = True
                        fila.append((nl, nc))


        return False
    

        


        