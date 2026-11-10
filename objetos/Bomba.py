import pygame
from objetos.Drops import gerar_drops_tile
from config import TELA_SIZE
from sons import tocar
from entidades.animacoes import desenhar_animacao
 
class Bomba:
    """bomba que o player planta: fica piscando um tempo e depois explode num losango ao redor."""
 
    def __init__(self, x, y, alcance_extra=0):
        self.rect         = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
        self.tempo_explosao = 180
        self.cor          = (0, 0, 0)
        self.explodiu     = False
        self.solida       = False
        self.alcance_extra = alcance_extra  # tiles extras de raio
        self.drops_gerados = []             # coletado pelo Blast_Miner
        self.efeito_timer = 0
        self.efeito_duracao = 18
 
    def atualizar(self, mapa, player, inimigos):
        if self.explodiu:
            if self.efeito_timer > 0:
                self.efeito_timer -= 1
            return

        if not self.solida:
            if not self.rect.colliderect(player.rect):
                self.solida = True
 
        if self.tempo_explosao < 60:
            self.cor = (255, 0, 0) if (self.tempo_explosao // 8) % 2 == 0 else (200, 50, 50)
        else:
            self.cor = (20, 20, 20)
 
        if self.tempo_explosao > 0:
            self.tempo_explosao -= 1
        else:
            if not self.explodiu:
                self.explodir(mapa, player, inimigos)
 
    def explodir(self, mapa, player, inimigos):
        # descobre em que tile (linha/coluna) o centro da bomba esta, pra calcular
        # o losango de explosao a partir dali
        self.explodiu = True
        self.solida = False
        self.efeito_timer = self.efeito_duracao
        tocar('explosao')
        col = self.rect.centerx // TELA_SIZE
        lin = self.rect.centery // TELA_SIZE
 
        # alcance base + extra por upgrade. base 1 -> 2: a bomba tava fraca de mais
        # (losango de 5 blocos so), com 2 ela cobre uma area bem mais util sem virar
        # a arma principal do jogo (a picareta continua sendo o dano confiavel)
        raio = 2 + self.alcance_extra
        alcance = []
        for dl in range(-raio, raio + 1):
            for dc in range(-raio, raio + 1):
                if abs(dl) + abs(dc) <= raio:  # losango (Manhattan)
                    alcance.append((dl, dc))
 
        inimigos_atingidos = set()

        for d_lin, d_col in alcance:
            alvo_l = lin + d_lin
            alvo_c = col + d_col
 
            if 0 <= alvo_l < len(mapa) and 0 <= alvo_c < len(mapa[0]):
                explosao_rect = pygame.Rect(alvo_c * TELA_SIZE, alvo_l * TELA_SIZE, TELA_SIZE, TELA_SIZE)
 
                if mapa[alvo_l][alvo_c] in (2, 4):
                    # gera drops antes de destruir o tile
                    drops = gerar_drops_tile(alvo_c, alvo_l, mapa[alvo_l][alvo_c])
                    self.drops_gerados.extend(drops)
                    mapa[alvo_l][alvo_c] = 0
 
                if player.rect.colliderect(explosao_rect):
                    player.receber_dano(30)
 
                for inimigo in inimigos:
                    identificador = id(inimigo)
                    if inimigo.ativo and identificador not in inimigos_atingidos and inimigo.rect.colliderect(explosao_rect):
                        inimigos_atingidos.add(identificador)
                        inimigo.receber_dano_explosao()
    def desenhar(self, tela, cam_x=0, cam_y=0):
        if self.explodiu:
            desenhar_animacao(
                tela, self, "bomba", "explosion", 76, cam_x, cam_y,
                intervalo=3,
            )
            return

        acao = "alert" if self.tempo_explosao < 60 else "idle"
        if not desenhar_animacao(
            tela, self, "bomba", acao, 38, cam_x, cam_y,
            intervalo=8 if acao == "alert" else 18,
        ):
            rect = pygame.Rect(self.rect.x - cam_x, self.rect.y - cam_y, self.rect.width, self.rect.height)
            pygame.draw.rect(tela, self.cor, rect)
