import pygame
import random
from entidades.Inimigo import Inimigo
from entidades.animacoes import desenhar_animacao
 
class CogumeloEsporos(Inimigo):
    """cogumelo parado no lugar (nunca anda), fica escondido e depois lanca um esporo venenoso."""
 
    COR_ESCONDIDO = (60, 80, 40)
    COR_NORMAL    = (100, 160, 60)
    COR_LANCAR    = (200, 80, 200)
 
    def __init__(self, x, y):
        # vida 3 -> 5. velocidade continua 0 porque ele e preso no chao (nao anda nunca)
        super().__init__(x, y, largura=40, altura=40, velocidade=0, vida=5, cor=self.COR_NORMAL)
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
 
    def receber_dano_picareta(self, dano, player_rect):
        # bug reportado: a espada empurrava esse cogumelo mesmo ele sendo preso no chao.
        # deixa a classe mae cuidar do dano/morte normalmente, e so cancela o empurrao no final.
        super().receber_dano_picareta(dano, player_rect)
        self.kb_dx = 0
        self.kb_dy = 0
        self.kb_timer = 0
 
    def desenhar(self, tela, cam_x=0, cam_y=0):
        if self.escondido and self.timer_escondido <= 30:
            acao = "attack"
        elif self.escondido:
            acao = "alert"
        else:
            acao = "hidden"
        if not desenhar_animacao(
            tela, self, "cogumelo_esporos", acao, 48, cam_x, cam_y,
            intervalo=8 if acao != "idle" else 14,
        ):
            rect = self.rect_na_tela(cam_x, cam_y)
            pygame.draw.rect(tela, self.cor, rect)
            chapeu = pygame.Rect(rect.x - 5, rect.y - 8, rect.width + 10, 12)
            pygame.draw.ellipse(tela, (180, 60, 60), chapeu)
 
 
class CogumeloAgressivo(Inimigo):
    """cogumelo que anda, persegue o player de longe e da uma investida rapida (dash) quando chega perto."""
 
    COR_NORMAL    = (140, 100, 40)
    COR_INVESTIDA = (220, 40, 40)
 
    def __init__(self, x, y):
        # ALTERAÇÃO: Velocidade reduzida de 2 para 1.2 para corrigir o balanceamento
        # vida 5 -> 8 pra nao morrer tao rapido
        super().__init__(x, y, largura=45, altura=45, velocidade=1.2, vida=8, cor=self.COR_NORMAL)
        self.raio_deteccao = 300
        self.cooldown_investida = 0
        self.investindo = False
        self.investida_dx = self.investida_dy = 0
        self.investida_timer = 0
        self.em_movimento = False
        self.sprite_invertido = False
        # direcao_patrulha/passos_patrulha ja vem prontos da classe mae (Inimigo.__init__)
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_antiga_x, pos_antiga_y = self.salvar_posicao()
        self.sprite_invertido = player.rect.centerx < self.rect.centerx
        dist = ((self.rect.centerx - player.rect.centerx)**2 + (self.rect.centery - player.rect.centery)**2) ** 0.5
 
        if self.investindo:
            # ta no meio da investida: so anda na linha reta calculada quando comecou o dash
            self.mover_x(self.investida_dx)
            self.mover_y(self.investida_dy)
            self.investida_timer -= 1
            for p in paredes:
                if self.rect.colliderect(p):
                    self.restaurar_posicao(pos_antiga_x, pos_antiga_y)
                    self.investindo = False
                    break
            if self.investida_timer <= 0:
                self.investindo = False
                self.cor = self.COR_NORMAL
            return
 
        if dist <= self.raio_deteccao:
            # perseguindo o player
            if self.rect.x < player.rect.x: self.mover_x(self.velocidade)
            elif self.rect.x > player.rect.x: self.mover_x(-self.velocidade)
            if self.rect.y < player.rect.y: self.mover_y(self.velocidade)
            elif self.rect.y > player.rect.y: self.mover_y(-self.velocidade)
 
            for p in paredes:
                if self.rect.colliderect(p):
                    self.restaurar_posicao(pos_antiga_x, pos_antiga_y)
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
            # fora de alcance: so patrulha (metodo generico da classe mae)
            self.cor = self.COR_NORMAL
            self._patrulhar_aleatorio(paredes, passos_max=80)
 
        if self.cooldown_investida > 0: self.cooldown_investida -= 1
        self.em_movimento = self.rect.topleft != (round(pos_antiga_x), round(pos_antiga_y))
 
    def desenhar(self, tela, cam_x=0, cam_y=0):
        if self.kb_timer > 0:
            acao = "hurt"
        elif self.investindo:
            acao = "attack"
        else:
            acao = "walk" if self.em_movimento else "idle"
        if not desenhar_animacao(
            tela, self, "cogumelo_agressivo", acao, 52, cam_x, cam_y,
            intervalo=7 if acao != "idle" else 13,
            inverter=self.sprite_invertido,
        ):
            rect = self.rect_na_tela(cam_x, cam_y)
            pygame.draw.rect(tela, self.cor, rect)
            chapeu = pygame.Rect(rect.x - 6, rect.y - 10, rect.width + 12, 14)
            pygame.draw.ellipse(tela, (80, 40, 160), chapeu)
