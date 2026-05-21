import pygame
from entidades.Inimigo import Inimigo
from objetos import Bomba


class Golem(Inimigo):
    COR_NORMAL  = (139, 90, 43)    # Marrom pedra
    COR_ALERTA  = (200, 60, 20)    # Laranja-avermelhado ao perseguir

    def __init__(self, x, y):
        # Chama o __init__ da classe mãe com os atributos do Golem
        super().__init__(
            x=x, y=y,
            largura=45, altura=45,
            velocidade=1,           # Mais lento que o Fantasma
            vida=5,                 # Mais resistente que o Fantasma
            cor=Golem.COR_NORMAL
        )
        self.raio_deteccao = 250    # Distância (px) para o Golem notar o player
        self.cooldown_knockback = 0 # Impede knockback consecutivo

    def _distancia_para(self, player):
        """Calcula a distância entre o Golem e o Player."""
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return (dx**2 + dy**2) ** 0.5

    #Sobrescrita do método abstrato da classe mãe
    def mover(self, player, paredes, mapa=None):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
        distancia = self._distancia_para(player)

        # Só age se o player estiver dentro do raio de detecção
        if distancia <= self.raio_deteccao:
            self.cor = Golem.COR_ALERTA

            # Persegue o player em X
            if self.rect.x < player.rect.x: self.rect.x += self.velocidade
            elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade

            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x = pos_antiga_x
                    break

            # Persegue o player em Y
            if self.rect.y < player.rect.y: self.rect.y += self.velocidade
            elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade

            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.y = pos_antiga_y
                    break
        else:
            self.cor = Golem.COR_NORMAL  # Fica parado fora do raio

        # Atualiza cooldown do knockback
        if self.cooldown_knockback > 0:
            self.cooldown_knockback -= 1

    def aplicar_knockback_no_player(self, player, paredes, bombas):
        """
        ao colidir com o player, empurra ele para longe além de causar dano.
        """
        if self.rect.colliderect(player.rect):
            player.receber_dano()
            if self.cooldown_knockback == 0:
                player.aplicar_knockback(self.rect, paredes, bombas)
                self.cooldown_knockback = 90  # Evita knockback spam (1,5s)
                print("[GOLEM] Knockback aplicado no Mike!")
