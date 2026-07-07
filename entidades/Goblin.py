
import pygame
import random
from entidades.Inimigo import Inimigo
 
class Goblin(Inimigo):
    COR_NORMAL  = (80, 160, 60)
    COR_FUGINDO = (180, 220, 80)
 
    def __init__(self, x, y):
        super().__init__(x, y, largura=38, altura=38, velocidade=3, vida=3, cor=self.COR_NORMAL)
        self.raio_ataque = 250
        self.cooldown_lanca = 0
        self.minerios_roubados = 0  # placeholder pra futura economia
        self.fugindo = False
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
 
        dist = ((self.rect.centerx - player.rect.centerx)**2 +
                (self.rect.centery - player.rect.centery)**2) ** 0.5
 
        if self.fugindo:
            # foge do player
            if self.rect.x > player.rect.x: self.rect.x += self.velocidade
            else: self.rect.x -= self.velocidade
            if self.rect.y > player.rect.y: self.rect.y += self.velocidade
            else: self.rect.y -= self.velocidade
            self.cor = self.COR_FUGINDO
        elif dist <= self.raio_ataque:
            # mantém distância e ataca à distância
            if dist < 150:
                # muito perto: recua
                if self.rect.x > player.rect.x: self.rect.x += self.velocidade
                else: self.rect.x -= self.velocidade
                if self.rect.y > player.rect.y: self.rect.y += self.velocidade
                else: self.rect.y -= self.velocidade
            # lança lança
            if self.cooldown_lanca <= 0:
                self.cooldown_lanca = 120
                self._lancar_lanca(player)
 
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x = pos_antiga_x
                self.rect.y = pos_antiga_y
                break
 
        if self.cooldown_lanca > 0:
            self.cooldown_lanca -= 1
 
    def _lancar_lanca(self, player):
        # dano simples instantâneo se dentro do raio (projétil simplificado)
        dist = ((self.rect.centerx - player.rect.centerx)**2 +
                (self.rect.centery - player.rect.centery)**2) ** 0.5
        if dist <= self.raio_ataque:
            player.receber_dano(15)
            print(f"[GOBLIN] Lançou lança! HP Mike: {player.hp}")
 
    def receber_dano_explosao(self):
        super().receber_dano_explosao()
        # ao morrer devolve minerios — placeholder
 
    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
        # orelha pontuda
        pontos = [
            (self.rect.centerx - 8, self.rect.top),
            (self.rect.centerx - 14, self.rect.top - 12),
            (self.rect.centerx - 2, self.rect.top),
        ]
        pygame.draw.polygon(tela, self.cor, pontos)
        pontos2 = [
            (self.rect.centerx + 8, self.rect.top),
            (self.rect.centerx + 14, self.rect.top - 12),
            (self.rect.centerx + 2, self.rect.top),
        ]
        pygame.draw.polygon(tela, self.cor, pontos2)