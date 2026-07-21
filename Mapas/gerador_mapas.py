import random
from collections import deque

# tiles:
# 0 = chão
# 1 = parede (inquebrável)
# 2 = pedra (quebrável)
# 3 = saída
# 4 = minério (quebrável)
# 5 = água (bloqueia movimento, inquebrável, projéteis/explosões passam)

class GeradorProcedural:
    LINHAS_BASE  = 18
    COLUNAS_BASE = 24
    LINHAS_MAX   = 36
    COLUNAS_MAX  = 52
    TELA_SIZE    = 50  # tamanho do tile em pixels (para calcular posicao de drops, spawn de inimigos, etc)

    def __init__(self):
        self.linhas  = self.LINHAS_BASE
        self.colunas = self.COLUNAS_BASE

    def _dimensoes_para_fase(self, fase_num):
        crescimento = fase_num - 1
        linhas  = min(self.LINHAS_BASE  + crescimento * 2, self.LINHAS_MAX)
        colunas = min(self.COLUNAS_BASE + crescimento * 3, self.COLUNAS_MAX)
        return linhas, colunas

    def gerar_fase(self, fase_num=1):
        self.linhas, self.colunas = self._dimensoes_para_fase(fase_num)
        print(f"[MAPA] Fase {fase_num} — {self.linhas}x{self.colunas}")
        for _ in range(20):
            mapa = self._gerar_tentativa(fase_num)
            if mapa and self.validar_caminho(mapa):
                return mapa
        return self._gerar_fallback()

    def _gerar_tentativa(self, fase_num):
        if   fase_num <= 3:  densidade = 0.48
        elif fase_num <= 6:  densidade = 0.44
        elif fase_num <= 9:  densidade = 0.40
        else:                densidade = 0.35

        mapa = self._gerar_ruido_inicial(densidade)
        mapa = self._suavizar(mapa, iteracoes=4)
        mapa = self._gerar_lagos_agua(mapa)
        mapa = self._abrir_zona_spawn(mapa)
        mapa = self._popular_recursos(mapa, fase_num)
        mapa = self._posicionar_saida(mapa)
        return mapa

    def _gerar_ruido_inicial(self, densidade_parede=0.45):
        mapa = []
        for l in range(self.linhas):
            linha = []
            for c in range(self.colunas):
                borda = (l == 0 or l == self.linhas - 1 or c == 0 or c == self.colunas - 1)
                linha.append(1 if borda or random.random() < densidade_parede else 0)
            mapa.append(linha)
        return mapa

    def _suavizar(self, mapa, iteracoes=4):
        for _ in range(iteracoes):
            novo = [linha[:] for linha in mapa]
            for l in range(1, self.linhas - 1):
                for c in range(1, self.colunas - 1):
                    if self._vizinhos_parede(mapa, l, c) >= 5:
                        novo[l][c] = 1
                    else:
                        novo[l][c] = 0
            mapa = novo
        return mapa

    def _vizinhos_parede(self, mapa, l, c):
        count = 0
        for dl in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dl == 0 and dc == 0: continue
                nl, nc = l + dl, c + dc
                if 0 <= nl < self.linhas and 0 <= nc < self.colunas:
                    count += mapa[nl][nc] == 1
                else:
                    count += 1
        return count
 
    def _gerar_lagos_agua(self, mapa):
        for l in range(2, self.linhas - 2):
            for c in range(2, self.colunas - 2):
                if mapa[l][c] == 0 and random.random() < 0.06:
                    mapa[l][c] = 5
        for _ in range(2):
            novo = [linha[:] for linha in mapa]
            for l in range(1, self.linhas - 1):
                for c in range(1, self.colunas - 1):
                    if mapa[l][c] in [0, 5]:
                        vizinhos_agua = sum(1 for dl in [-1,0,1] for dc in [-1,0,1] if mapa[l+dl][c+dc] == 5)
                        if vizinhos_agua >= 4: novo[l][c] = 5
                        elif vizinhos_agua < 2 and mapa[l][c] == 5: novo[l][c] = 0
            mapa = novo
        return mapa
 
    def _abrir_zona_spawn(self, mapa):
        for l in range(1, 5):
            for c in range(1, 5):
                mapa[l][c] = 0
        return mapa
 
    def _popular_recursos(self, mapa, fase_num):
        chance_pedra = 0.25 if fase_num <= 3 else (0.18 if fase_num <= 6 else 0.12)
        zona_segura = {(l, c) for l in range(1, 5) for c in range(1, 5)}
 
        for l in range(1, self.linhas - 1):
            for c in range(1, self.colunas - 1):
                if mapa[l][c] == 0 and (l, c) not in zona_segura:
                    if random.random() < chance_pedra:
                        mapa[l][c] = 2
 
        for _ in range(random.randint(2, 5)):
            l_v, c_v = random.randint(4, self.linhas - 3), random.randint(5, self.colunas - 4)
            for _ in range(random.randint(2, 5)):
                if 0 <= l_v < self.linhas and 0 <= c_v < self.colunas:
                    if mapa[l_v][c_v] in [0, 2, 5] and (l_v, c_v) not in zona_segura:
                        mapa[l_v][c_v] = 4
                l_v = max(1, min(self.linhas - 2,  l_v + random.choice([-1, 0, 1])))
                c_v = max(1, min(self.colunas - 2, c_v + random.choice([-1, 0, 1])))
        return mapa
 
    def _posicionar_saida(self, mapa):
        candidatas = [(l, c) for l in range(self.linhas) for c in range(self.colunas)
                      if mapa[l][c] == 0 and abs(l - 1) + abs(c - 1) >= 8 and l >= self.linhas//3 and c >= self.colunas//3]
        if candidatas:
            l_s, c_s = random.choice(candidatas)
            mapa[l_s][c_s] = 3
            for dl in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if mapa[l_s+dl][c_s+dc] == 5: mapa[l_s+dl][c_s+dc] = 0
        else:
            mapa[self.linhas - 2][self.colunas - 2] = 3
        return mapa
 
    def _gerar_fallback(self):
        mapa = [[0] * self.colunas for _ in range(self.linhas)]
        for l in range(self.linhas):
            for c in range(self.colunas):
                if l == 0 or l == self.linhas - 1 or c == 0 or c == self.colunas - 1: mapa[l][c] = 1
        mapa[self.linhas - 2][self.colunas - 2] = 3
        return mapa
 
    def validar_caminho(self, mapa):
        linhas, colunas = len(mapa), len(mapa[0])
        visitados = [[False] * colunas for _ in range(linhas)]
        fila = deque([(1, 1)])
        visitados[1][1] = True
 
        while fila:
            l, c = fila.popleft()
            if mapa[l][c] == 3: return True
            for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nl, nc = l + dl, c + dc
                if 0 <= nl < linhas and 0 <= nc < colunas:
                    if not visitados[nl][nc] and mapa[nl][nc] not in [1, 5]:
                        visitados[nl][nc] = True
                        fila.append((nl, nc))
        return False
 
    def listar_chao_livre_acessivel(self, mapa, excluir_raio=0, origem=(1, 1)):
        linhas, colunas = len(mapa), len(mapa[0])
        acessiveis = []
        visitados = [[False] * colunas for _ in range(linhas)]
        fila = deque([origem])
        visitados[origem[0]][origem[1]] = True
 
        while fila:
            l, c = fila.popleft()
            if mapa[l][c] == 0 and (abs(l - origem[0]) + abs(c - origem[1]) > excluir_raio):
                acessiveis.append((l, c))
            for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nl, nc = l + dl, c + dc
                if 0 <= nl < linhas and 0 <= nc < colunas:
                    if not visitados[nl][nc] and mapa[nl][nc] not in [1, 5]:
                        visitados[nl][nc] = True
                        fila.append((nl, nc))
        return acessiveis
 
    def achar_vagas_vendedores_bfs(self, mapa, l_saida, c_saida):
        """NOVA MELHORIA: Varre ao redor da saída por BFS para achar 2 blocos de chão (0) perfeitamente acessíveis."""
        linhas, colunas = len(mapa), len(mapa[0])
        visitados = [[False] * colunas for _ in range(linhas)]
        fila = deque([(l_saida, c_saida)])
        visitados[l_saida][c_saida] = True
        vagas = []
 
        while fila and len(vagas) < 2:
            l, c = fila.popleft()
            if mapa[l][c] == 0:
                vagas.append((l, c))
            for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nl, nc = l + dl, c + dc
                if 0 <= nl < linhas and 0 <= nc < colunas:
                    if not visitados[nl][nc] and mapa[nl][nc] != 1:
                        visitados[nl][nc] = True
                        fila.append((nl, nc))
        return vagas
