import pygame
import random
from entidades.Inimigo import Inimigo
from entidades.animacoes import desenhar_animacao
 
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
        self.em_movimento = False
        self.ataque_sprite_timer = 0
        self.sprite_invertido = False
        # direcao_patrulha/passos_patrulha ja vem prontos da classe mae (Inimigo.__init__)
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_antiga_x, pos_antiga_y = self.salvar_posicao()
        dx_player = player.rect.centerx - self.rect.centerx
        self.sprite_invertido = dx_player < 0
        dist = ((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2) ** 0.5
 
        if self.fugindo:
            if self.rect.x > player.rect.x: self.mover_x(self.velocidade)
            else: self.mover_x(-self.velocidade)
            if self.rect.y > player.rect.y: self.mover_y(self.velocidade)
            else: self.mover_y(-self.velocidade)
            self.cor = self.COR_FUGINDO
        # ALTERAÇÃO: Se avistar, ataca/recua. Caso contrário, patrulha livremente.
        elif dist <= self.raio_ataque:
            self.cor = self.COR_NORMAL
            if dist < 150:
                if self.rect.x > player.rect.x: self.mover_x(self.velocidade)
                else: self.mover_x(-self.velocidade)
                if self.rect.y > player.rect.y: self.mover_y(self.velocidade)
                else: self.mover_y(-self.velocidade)
            if self.cooldown_lanca <= 0:
                self.cooldown_lanca = 120
                self.ataque_sprite_timer = 24
                self.projeteis_pendentes.append((self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery))
        else:
            # fora de alcance: usa a patrulha generica da classe mae em vez de logica propria
            self.cor = self.COR_NORMAL
            self._patrulhar_aleatorio(paredes, passos_max=70)
 
        # trava geral: se em qualquer um dos casos acima o goblin acabou entrando numa
        # parede, desfaz o movimento (a patrulha ja se resolve sozinha, mas fugindo/atacando nao)
        for p in paredes:
            if self.rect.colliderect(p):
                self.restaurar_posicao(pos_antiga_x, pos_antiga_y)
                break
 
        if self.cooldown_lanca > 0: self.cooldown_lanca -= 1
        self.em_movimento = self.rect.topleft != (round(pos_antiga_x), round(pos_antiga_y))
        if self.ataque_sprite_timer > 0:
            self.ataque_sprite_timer -= 1
 
    def desenhar(self, tela, cam_x=0, cam_y=0):
        if self.kb_timer > 0:
            acao = "hurt"
        elif self.ataque_sprite_timer > 0:
            acao = "attack"
        else:
            acao = "walk" if self.em_movimento else "idle"
        if not desenhar_animacao(
            tela, self, "goblin", acao, 50, cam_x, cam_y,
            intervalo=7 if acao != "idle" else 13,
            inverter=self.sprite_invertido,
        ):
            super().desenhar(tela, cam_x, cam_y)
