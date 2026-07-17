import pygame
import random
from entidades.Inimigo import Inimigo

class Golem(Inimigo):
    COR_NORMAL  = (139, 90, 43)    
    COR_ALERTA  = (200, 60, 20)    

    def __init__(self, x, y):
        super().__init__(x=x, y=y, largura=45, altura=45, velocidade=1, vida=5, cor=self.COR_NORMAL)
        self.raio_deteccao = 250    
        self.cooldown_knockback = 0 
        # ALTERAÇÃO: Adicionado direções de patrulha livre para o Golem
        self.direcao_patrulha = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
        self.passos_patrulha = 0

    def _distancia_para(self, player):
        return ((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2) ** 0.5

    def mover(self, player, paredes, mapa, bomba=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_antiga_x, pos_antiga_y = self.rect.x, self.rect.y
        distancia = self._distancia_para(player)

        # ALTERAÇÃO: Se o player estiver no raio, persegue. Caso contrário, patrulha livremente.
        if distancia <= self.raio_deteccao:
            self.cor = Golem.COR_ALERTA
            if self.rect.x < player.rect.x: self.rect.x += self.velocidade
            elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x = pos_antiga_x
                    break

            if self.rect.y < player.rect.y: self.rect.y += self.velocidade
            elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.y = pos_antiga_y
                    break
        else:
            # Patrulha Livre
            self.cor = Golem.COR_NORMAL  
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
            if self.passos_patrulha > 100:
                self.direcao_patrulha = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                self.passos_patrulha = 0

        if self.cooldown_knockback > 0: self.cooldown_knockback -= 1

    def aplicar_knockback_no_player(self, player, paredes, bombas):
        if self.rect.colliderect(player.rect):
            player.receber_dano()
            if self.cooldown_knockback == 0:
                player.aplicar_knockback(self.rect, paredes, bombas)
                self.cooldown_knockback = 90  
                print("[GOLEM] Knockback aplicado no Mike!")