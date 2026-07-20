import pygame
import random
from entidades.Inimigo import Inimigo
 
class Goblin(Inimigo):
    """goblin com lanca: patrulha livre, e quando ve o player entra no modo ataque (aproxima e joga lanca)."""
 
    COR_NORMAL  = (80, 160, 60)
    COR_FUGINDO = (180, 220, 80)
 
    def __init__(self, x, y):
        # vida 3 -> 6
        super().__init__(x, y, largura=38, altura=38, velocidade=3, vida=6, cor=self.COR_NORMAL)
        self.raio_ataque = 250
        self.cooldown_lanca = 0
        self.fugindo = False
        self.projeteis_pendentes = []  
        # direcao_patrulha/passos_patrulha ja vem prontos da classe mae (Inimigo.__init__)
 
    def mover(self, player, paredes, mapa=None, bombs=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_antiga_x, pos_antiga_y = self.rect.x, self.rect.y
        dist = ((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2) ** 0.5
 
        if self.fugindo:
            if self.rect.x > player.rect.x: self.rect.x += self.velocidade
            else: self.rect.x -= self.velocidade
            if self.rect.y > player.rect.y: self.rect.y += self.velocidade
            else: self.rect.y -= self.velocidade
            self.cor = self.COR_FUGINDO
        # ALTERAÇÃO: Se avistar, ataca/recua. Caso contrário, patrulha livremente.
        elif dist <= self.raio_ataque:
            self.cor = self.COR_NORMAL
            if dist < 150:
                if self.rect.x > player.rect.x: self.rect.x += self.velocidade
                else: self.rect.x -= self.velocidade
                if self.rect.y > player.rect.y: self.rect.y += self.velocidade
                else: self.rect.y -= self.velocidade
            if self.cooldown_lanca <= 0:
                self.cooldown_lanca = 120
                self.projeteis_pendentes.append((self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery))
        else:
            # fora de alcance: usa a patrulha generica da classe mae em vez de logica propria
            self.cor = self.COR_NORMAL
            self._patrulhar_aleatorio(paredes, passos_max=70)
 
        # trava geral: se em qualquer um dos casos acima o goblin acabou entrando numa
        # parede, desfaz o movimento (a patrulha ja se resolve sozinha, mas fugindo/atacando nao)
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x, self.rect.y = pos_antiga_x, pos_antiga_y
                break
 
        if self.cooldown_lanca > 0: self.cooldown_lanca -= 1
 
    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
        pontos = [(self.rect.centerx - 8, self.rect.top), (self.rect.centerx - 14, self.rect.top - 12), (self.rect.centerx - 2, self.rect.top)]
        pygame.draw.polygon(tela, self.cor, pontos)
        pontos2 = [(self.rect.centerx + 8, self.rect.top), (self.rect.centerx + 14, self.rect.top - 12), (self.rect.centerx + 2, self.rect.top)]
        pygame.draw.polygon(tela, self.cor, pontos2)
