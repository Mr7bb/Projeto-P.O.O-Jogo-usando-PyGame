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
    # tamanho base; cada fase adiciona +2 linhas e +3 colunas até um limite
    LINHAS_BASE  = 18
    COLUNAS_BASE = 24
    LINHAS_MAX   = 36
    COLUNAS_MAX  = 52

    def __init__(self):
        self.linhas  = self.LINHAS_BASE
        self.colunas = self.COLUNAS_BASE

    def _dimensoes_para_fase(self, fase_num):
        """Cresce o mapa progressivamente a cada fase."""
        crescimento = fase_num - 1
        linhas  = min(self.LINHAS_BASE  + crescimento * 2, self.LINHAS_MAX)
        colunas = min(self.COLUNAS_BASE + crescimento * 3, self.COLUNAS_MAX)
        return linhas, colunas

    def gerar_fase(self, fase_num=1):
        self.linhas, self.colunas = self._dimensoes_para_fase(fase_num)
        print(f"[MAPA] Fase {fase_num} — {self.linhas}x{self.colunas}")
        # tenta gerar até 20 vezes até passar na validação BFS
        for _ in range(20):
            mapa = self._gerar_tentativa(fase_num)
            if mapa and self.validar_caminho(mapa):
                return mapa
        return self._gerar_fallback()

    # --- geração ---

    def _gerar_tentativa(self, fase_num):
        # fases mais avançadas = cavernas mais abertas (mais espaço pra combate)
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
        # preenche aleatoriamente — bordas são sempre parede
        mapa = []
        for l in range(self.linhas):
            linha = []
            for c in range(self.colunas):
                borda = (l == 0 or l == self.linhas - 1
                         or c == 0 or c == self.colunas - 1)
                linha.append(1 if borda or random.random() < densidade_parede else 0)
            mapa.append(linha)
        return mapa

    def _suavizar(self, mapa, iteracoes=4):
        # cellular automata: célula com >= 5 vizinhos parede vira parede, senão vira chão
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
                if dl == 0 and dc == 0:
                    continue
                nl, nc = l + dl, c + dc
                if 0 <= nl < self.linhas and 0 <= nc < self.colunas:
                    count += mapa[nl][nc] == 1
                else:
                    count += 1  # fora do mapa conta como parede
        return count

    def _gerar_lagos_agua(self, mapa):
        """Gera pequenos lagos orgânicos onde há chão livre utilizando autômatos celulares."""
        for l in range(2, self.linhas - 2):
            for c in range(2, self.colunas - 2):
                if mapa[l][c] == 0 and random.random() < 0.07:
                    mapa[l][c] = 5  # semente de água

        for _ in range(2):
            novo = [linha[:] for linha in mapa]
            for l in range(1, self.linhas - 1):
                for c in range(1, self.colunas - 1):
                    if mapa[l][c] in [0, 5]:
                        vizinhos_agua = 0
                        for dl in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if 0 <= l+dl < self.linhas and 0 <= c+dc < self.colunas:
                                    if mapa[l+dl][c+dc] == 5:
                                        vizinhos_agua += 1
                        if vizinhos_agua >= 4:
                            novo[l][c] = 5
                        elif vizinhos_agua < 2 and mapa[l][c] == 5:
                            novo[l][c] = 0
            mapa = novo
        return mapa

    def _abrir_zona_spawn(self, mapa):
        # garante 4x4 limpo (sem água ou parede) no canto superior esquerdo pro Mike aparecer
        for l in range(1, 5):
            for c in range(1, 5):
                mapa[l][c] = 0
        return mapa

    def _popular_recursos(self, mapa, fase_num):
        if   fase_num <= 3:  chance_pedra = 0.25
        elif fase_num <= 6:  chance_pedra = 0.20
        elif fase_num <= 9:  chance_pedra = 0.15
        else:                chance_pedra = 0.10

        zona_segura = {(l, c) for l in range(1, 5) for c in range(1, 5)}

        for l in range(1, self.linhas - 1):
            for c in range(1, self.colunas - 1):
                if mapa[l][c] == 0 and (l, c) not in zona_segura:
                    if random.random() < chance_pedra:
                        mapa[l][c] = 2

        # veios de minério
        for _ in range(random.randint(2, 5)):
            l_v = random.randint(4, self.linhas - 3)
            c_v = random.randint(5, self.colunas - 4)
            for _ in range(random.randint(2, 5)):
                if 0 <= l_v < self.linhas and 0 <= c_v < self.colunas:
                    if mapa[l_v][c_v] in [0, 2, 5] and (l_v, c_v) not in zona_segura:
                        mapa[l_v][c_v] = 4
                l_v = max(1, min(self.linhas - 2,  l_v + random.choice([-1, 0, 1])))
                c_v = max(1, min(self.colunas - 2, c_v + random.choice([-1, 0, 1])))

        return mapa

    def _posicionar_saida(self, mapa):
        candidatas = [
            (l, c)
            for l in range(self.linhas)
            for c in range(self.colunas)
            if mapa[l][c] == 0
            and abs(l - 1) + abs(c - 1) >= 8
            and l >= self.linhas  // 3
            and c >= self.colunas // 3
        ]

        if candidatas:
            l_s, c_s = random.choice(candidatas)
            mapa[l_s][c_s] = 3
            # Garante que ao redor da saída não terá água sufocando o acesso
            for dl in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if mapa[l_s+dl][c_s+dc] == 5:
                        mapa[l_s+dl][c_s+dc] = 0
        else:
            for l in range(self.linhas - 2, 0, -1):
                if mapa[l][self.colunas - 2] not in [1, 5]:
                    mapa[l][self.colunas - 2] = 3
                    break

        return mapa

    def _gerar_fallback(self):
        mapa = [[0] * self.colunas for _ in range(self.linhas)]
        for l in range(self.linhas):
            for c in range(self.colunas):
                if l == 0 or l == self.linhas - 1 or c == 0 or c == self.colunas - 1:
                    mapa[l][c] = 1
        for l in range(3, self.linhas - 2):
            for c in range(5, self.colunas - 3):
                if random.random() < 0.15:
                    mapa[l][c] = 2
        mapa[self.linhas - 2][self.colunas - 2] = 3
        return mapa

    def validar_caminho(self, mapa):
        # BFS do spawn (1,1) até a saída (tile 3)
        # Pedras (2, 4) são transponíveis porque são quebráveis. Água (5) e Parede (1) bloqueiam.
        linhas  = len(mapa)
        colunas = len(mapa[0])
        visitados = [[False] * colunas for _ in range(linhas)]

        fila = deque([(1, 1)])
        visitados[1][1] = True

        while fila:
            l, c = fila.popleft()
            if mapa[l][c] == 3:
                return True
            for dl, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nl, nc = l + dl, c + dc
                if 0 <= nl < linhas and 0 <= nc < colunas:
                    # Água (5) e parede (1) não são transitáveis no BFS inicial do jogador
                    if not visitados[nl][nc] and mapa[nl][nc] not in [1, 5]:
                        visitados[nl][nc] = True
                        fila.append((nl, nc))
        return False

    def listar_chao_livre(self, mapa, excluir_raio=0, origem=(1, 1)):
        ol, oc = origem
        return [
            (l, c)
            for l in range(1, len(mapa) - 1)
            for c in range(1, len(mapa[0]) - 1)
            if mapa[l][c] == 0 and abs(l - ol) + abs(c - oc) > excluir_raio
        ]