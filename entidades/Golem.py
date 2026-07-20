import pygame
from entidades.Inimigo import Inimigo
 
class Golem(Inimigo):
    """golem de pedra: lento, tanque, e da um empurrao forte (knockback) quando encosta no player."""
 
    COR_NORMAL  = (139, 90, 43)    
    COR_ALERTA  = (200, 60, 20)    
 
    def __init__(self, x, y):
        # vida 5 -> 8: ele era o mob mais tanque mas ainda assim morria rapido demais
        super().__init__(x=x, y=y, largura=45, altura=45, velocidade=1, vida=8, cor=self.COR_NORMAL)
        self.raio_deteccao = 250    
        self.cooldown_knockback = 0 
 
    def _distancia_para(self, player):
        return ((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2) ** 0.5
 
    def mover(self, player, paredes, mapa, bomba=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_antiga_x, pos_antiga_y = self.rect.x, self.rect.y
        distancia = self._distancia_para(player)
 
        if distancia <= self.raio_deteccao:
            # player detectado: larga a patrulha e vai direto pra cima dele
            self.cor = self.COR_ALERTA
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
            # fora do alcance: fica so patrulhando (metodo generico da classe mae)
            self.cor = self.COR_NORMAL
            self._patrulhar_aleatorio(paredes, passos_max=100)
 
        if self.cooldown_knockback > 0: self.cooldown_knockback -= 1
 
    def aplicar_knockback_no_player(self, player, paredes, bombas):
        # so acontece quando o golem realmente encosta no player (nao e ataque a distancia)
        if self.rect.colliderect(player.rect):
            player.receber_dano()
            if self.cooldown_knockback == 0:
                player.aplicar_knockback(self.rect, paredes, bombas)
                self.cooldown_knockback = 90  
                print("[GOLEM] Knockback aplicado no Mike!")