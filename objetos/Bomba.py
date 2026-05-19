import pygame

class Bomba:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.tempo_explosao = 240   # 4 segundos a 60fps
        self.cor = (0, 0, 0)
        self.explodiu = False
        self.solida = False         # Vira sólida após o player sair de cima

    def atualizar(self, mapa, player, inimigos):
        # Lógica para a bomba virar um obstáculo sólido
        if not self.solida:
            if not self.rect.colliderect(player.rect):
                self.solida = True

        # Efeito visual: bomba pisca quando está prestes a explodir
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
        alcance = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]

        for d_lin, d_col in alcance:
            alvo_l = lin + d_lin
            alvo_c = col + d_col

            if 0 <= alvo_l < len(mapa) and 0 <= alvo_c < len(mapa[0]):
                explosao_rect = pygame.Rect(alvo_c * 50, alvo_l * 50, 50, 50)

                # Destruir minério
                if mapa[alvo_l][alvo_c] == 2:
                    mapa[alvo_l][alvo_c] = 0

                # Dano no Player
                if player.rect.colliderect(explosao_rect):
                    player.receber_dano()

                # Dano nos Inimigos
                for inimigo in inimigos:
                    if inimigo.rect.colliderect(explosao_rect):
                        inimigo.receber_dano_explosao()