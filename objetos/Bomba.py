import pygame
from objetos.Drops import gerar_drops_tile

class Bomba:
    def __init__(self, x, y, alcance_extra=0):
        self.rect         = pygame.Rect(x, y, 50, 50)
        self.tempo_explosao = 180
        self.cor          = (0, 0, 0)
        self.explodiu     = False
        self.solida       = False
        self.alcance_extra = alcance_extra  # tiles extras de raio
        self.drops_gerados = []             # coletado pelo Blast_Miner

    def atualizar(self, mapa, player, inimigos):
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
        self.explodiu = True
        col = self.rect.centerx // 50
        lin = self.rect.centery // 50

        # alcance base + extra por upgrade
        raio = 1 + self.alcance_extra
        alcance = []
        for dl in range(-raio, raio + 1):
            for dc in range(-raio, raio + 1):
                if abs(dl) + abs(dc) <= raio:  # losango (Manhattan)
                    alcance.append((dl, dc))

        for d_lin, d_col in alcance:
            alvo_l = lin + d_lin
            alvo_c = col + d_col

            if 0 <= alvo_l < len(mapa) and 0 <= alvo_c < len(mapa[0]):
                explosao_rect = pygame.Rect(alvo_c * 50, alvo_l * 50, 50, 50)

                if mapa[alvo_l][alvo_c] in (2, 4):
                    # gera drops antes de destruir o tile
                    drops = gerar_drops_tile(alvo_c, alvo_l, mapa[alvo_l][alvo_c])
                    self.drops_gerados.extend(drops)
                    mapa[alvo_l][alvo_c] = 0

                if player.rect.colliderect(explosao_rect):
                    player.receber_dano(30)

                for inimigo in inimigos:
                    if inimigo.rect.colliderect(explosao_rect):
                        inimigo.receber_dano_explosao()