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
        self.timer_escondido = 0  # conta down antes de lançar esporo
        self.escondido = False
        self.dano_veneno = 5       # dano por tick de veneno
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        # fixo — só reage à proximidade do player
        dist = ((self.rect.centerx - player.rect.centerx)**2 +
                (self.rect.centery - player.rect.centery)**2) ** 0.5
 
        if dist <= self.raio_deteccao and not self.escondido:
            self.escondido = True
            self.timer_escondido = 120  # 2s escondido antes de atacar
            self.cor = self.COR_ESCONDIDO
            print("[COGUMELO-ESPORO] Se escondeu!")
 
        if self.escondido:
            self.timer_escondido -= 1
            if self.timer_escondido <= 30:
                self.cor = self.COR_LANCAR  # pisca antes de lançar
            if self.timer_escondido <= 0:
                self.escondido = False
                self.cor = self.COR_NORMAL
                # aplica veneno se player estiver no raio de explosão (150px)
                dist_exp = ((self.rect.centerx - player.rect.centerx)**2 +
                            (self.rect.centery - player.rect.centery)**2) ** 0.5
                if dist_exp <= 150:
                    player.receber_dano(10)
                    print("[COGUMELO-ESPORO] Lançou esporos! Player envenenado.")
                    # veneno: dano contínuo gerenciado externamente via flag
                    player._veneno_timer = 180  # 3s de veneno (gerenciado em Blast_Miner)
 
    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
        # chapéu do cogumelo
        chapeu = pygame.Rect(self.rect.x - 5, self.rect.y - 8, self.rect.width + 10, 12)
        pygame.draw.ellipse(tela, (180, 60, 60), chapeu)
 
 
class CogumeloAgressivo(Inimigo):
    COR_NORMAL   = (140, 100, 40)
    COR_INVESTIDA = (220, 40, 40)
 
    def __init__(self, x, y):
        super().__init__(x, y, largura=45, altura=45, velocidade=2, vida=5, cor=self.COR_NORMAL)
        self.raio_deteccao = 300
        self.cooldown_investida = 0
        self.investindo = False
        self.investida_dx = 0
        self.investida_dy = 0
        self.investida_timer = 0
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
 
        dist = ((self.rect.centerx - player.rect.centerx)**2 +
                (self.rect.centery - player.rect.centery)**2) ** 0.5
 
        if self.investindo:
            self.rect.x += self.investida_dx
            self.rect.y += self.investida_dy
            self.investida_timer -= 1
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x = pos_antiga_x
                    self.rect.y = pos_antiga_y
                    self.investindo = False
                    break
            if self.investida_timer <= 0:
                self.investindo = False
                self.cor = self.COR_NORMAL
            return
 
        if dist <= self.raio_deteccao:
            # movimento normal de perseguição
            if self.rect.x < player.rect.x: self.rect.x += self.velocidade
            elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade
            if self.rect.y < player.rect.y: self.rect.y += self.velocidade
            elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade
 
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x = pos_antiga_x
                    self.rect.y = pos_antiga_y
                    break
 
            # chance de investida
            if self.cooldown_investida <= 0 and dist <= 200:
                self.cooldown_investida = 180
                self.investindo = True
                self.investida_timer = 20
                self.cor = self.COR_INVESTIDA
                # direção da investida
                mag = max(dist, 1)
                self.investida_dx = int((player.rect.centerx - self.rect.centerx) / mag * 8)
                self.investida_dy = int((player.rect.centery - self.rect.centery) / mag * 8)
                print("[COGUMELO-AGR] Investida!")
 
        if self.cooldown_investida > 0:
            self.cooldown_investida -= 1
 
    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
        chapeu = pygame.Rect(self.rect.x - 6, self.rect.y - 10, self.rect.width + 12, 14)
        pygame.draw.ellipse(tela, (80, 40, 160), chapeu)