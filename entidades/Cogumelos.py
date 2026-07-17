import pygame
import random
from entidades.Inimigo import Inimigo

class CogumeloEsporos(Inimigo):
    COR_ESCONDIDO = (60, 80, 40)
    COR_NORMAL    = (100, 160, 60)
    COR_LANCAR    = (200, 80, 200)

    def __init__(self, x, y):
        super().__init__(x, y, largura=40, altura=40, velocidade=0, vida=3, cor=self.COR_NORMAL)
        self.raio_deteccao = 200
        self.timer_escondido = 0
        self.escondido = False
        self.projeteis_pendentes = []  

    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        dist = ((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2) ** 0.5

        if dist <= self.raio_deteccao and not self.escondido:
            self.escondido = True
            self.timer_escondido = 120
            self.cor = self.COR_ESCONDIDO

        if self.escondido:
            self.timer_escondido -= 1
            if self.timer_escondido <= 30: self.cor = self.COR_LANCAR
            if self.timer_escondido <= 0:
                self.escondido = False
                self.cor = self.COR_NORMAL
                self.projeteis_pendentes.append((self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery))

    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
        chapeu = pygame.Rect(self.rect.x - 5, self.rect.y - 8, self.rect.width + 10, 12)
        pygame.draw.ellipse(tela, (180, 60, 60), chapeu)


class CogumeloAgressivo(Inimigo):
    COR_NORMAL    = (140, 100, 40)
    COR_INVESTIDA = (220, 40, 40)

    def __init__(self, x, y):
        # ALTERAÇÃO: Velocidade reduzida de 2 para 1.2 para corrigir o balanceamento
        super().__init__(x, y, largura=45, altura=45, velocidade=1.2, vida=5, cor=self.COR_NORMAL)
        self.raio_deteccao = 300
        self.cooldown_investida = 0
        self.investindo = False
        self.investida_dx = self.investida_dy = 0
        self.investida_timer = 0
        self.direcao_patrulha = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
        self.passos_patrulha = 0

    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_antiga_x, pos_antiga_y = self.rect.x, self.rect.y
        dist = ((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2) ** 0.5

        if self.investindo:
            self.rect.x += self.investida_dx
            self.rect.y += self.investida_dy
            self.investida_timer -= 1
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x, self.rect.y = pos_antiga_x, pos_antiga_y
                    self.investindo = False
                    break
            if self.investida_timer <= 0:
                self.investindo = False
                self.cor = self.COR_NORMAL
            return

        if dist <= self.raio_deteccao:
            if self.rect.x < player.rect.x: self.rect.x += self.velocidade
            elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade
            if self.rect.y < player.rect.y: self.rect.y += self.velocidade
            elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade

            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x, self.rect.y = pos_antiga_x, pos_antiga_y
                    break

            if self.cooldown_investida <= 0 and dist <= 200:
                self.cooldown_investida = 180
                self.investindo = True
                self.investida_timer = 20
                self.cor = self.COR_INVESTIDA
                mag = max(dist, 1)
                self.investida_dx = int((player.rect.centerx - self.rect.centerx) / mag * 8)
                self.investida_dy = int((player.rect.centery - self.rect.centery) / mag * 8)
        else:
            self.cor = self.COR_NORMAL
            if self.direcao_patrulha == 'cima': self.rect.y -= self.velocidade
            elif self.direcao_patrulha == 'baixo': self.rect.y += self.velocidade
            elif self.direcao_patrulha == 'esquerda': self.rect.x -= self.velocidade
            elif self.direcao_patrulha == 'direita': self.rect.x += self.velocidade

            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x, self.rect.y = pos_antiga_x, pos_antiga_y
                    self.direcao_patrulha = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                    break
            self.passos_patrulha += 1
            if self.passos_patrulha > 80:
                self.direcao_patrulha = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                self.passos_patrulha = 0

        if self.cooldown_investida > 0: self.cooldown_investida -= 1

    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
        chapeu = pygame.Rect(self.rect.x - 6, self.rect.y - 10, self.rect.width + 12, 14)
        pygame.draw.ellipse(tela, (80, 40, 160), chapeu)