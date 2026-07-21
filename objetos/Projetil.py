import pygame
 
class Projetil:
    def __init__(self, x, y, alvo_x, alvo_y, velocidade, dano, cor, raio=6, veneno=False):
        self.rect = pygame.Rect(x, y, raio * 2, raio * 2)
        self.raio = raio
        self.dano = dano
        self.cor = cor
        self.veneno = veneno
        self.ativo = True
 
        dx = alvo_x - x
        dy = alvo_y - y
        dist = max((dx**2 + dy**2) ** 0.5, 1)
        self.vx = dx / dist * velocidade
        self.vy = dy / dist * velocidade
 
    def atualizar(self, player, paredes):
        self.rect.x += self.vx
        self.rect.y += self.vy
 
        if self.rect.colliderect(player.rect):
            player.receber_dano(self.dano)
            if self.veneno:
                player._veneno_timer = 180
            self.ativo = False
            return
 
        for p in paredes:
            if self.rect.colliderect(p):
                self.ativo = False
                return
 
        if (self.rect.x < -200 or self.rect.x > 4000 or
                self.rect.y < -200 or self.rect.y > 4000):
            self.ativo = False
 
    def desenhar(self, tela, cam_x=0, cam_y=0):
        cx = int(self.rect.centerx - cam_x)
        cy = int(self.rect.centery - cam_y)
        pygame.draw.circle(tela, self.cor, (cx, cy), self.raio)
        brilho = tuple(min(v + 80, 255) for v in self.cor)
        pygame.draw.circle(tela, brilho, (cx, cy), max(self.raio - 3, 1))
 
 
class Esporo(Projetil):
    COR = (160, 80, 200)
 
    def __init__(self, x, y, alvo_x, alvo_y):
        super().__init__(x, y, alvo_x, alvo_y,
                         velocidade=3, dano=10, cor=self.COR, raio=7, veneno=True)
 
 
class PicaretaFantasma(Projetil):
    """
    ataque "Picareta Fantasma" do boss Eco Perdido: um projetil espectral que atravessa
    parede (nao para em bloco solido, so some longe do mapa ou ao acertar o player).
    versao simplificada do bumerangue descrito no documento de design (o bumerangue
    voltando pro boss precisaria de uma referencia de volta que o sistema de projeteis
    generico do jogo nao tem hoje) -- aqui ele so atravessa tudo e desaparece no fim
    do percurso, que ja cobre a ideia central: "ataque espectral que ignora parede".
    """
    COR = (210, 190, 255)
 
    def __init__(self, x, y, alvo_x, alvo_y):
        super().__init__(x, y, alvo_x, alvo_y, velocidade=6, dano=20, cor=self.COR, raio=8, veneno=False)
 
    def atualizar(self, player, paredes):
        # igual ao Projetil normal, so que sem checar colisao com paredes
        self.rect.x += self.vx
        self.rect.y += self.vy
 
        if self.rect.colliderect(player.rect):
            player.receber_dano(self.dano)
            self.ativo = False
            return
 
        if (self.rect.x < -300 or self.rect.x > 5000 or
                self.rect.y < -300 or self.rect.y > 5000):
            self.ativo = False
 
    def desenhar(self, tela, cam_x=0, cam_y=0):
        cx = int(self.rect.centerx - cam_x)
        cy = int(self.rect.centery - cam_y)
        pygame.draw.circle(tela, self.cor, (cx, cy), self.raio)
        pygame.draw.circle(tela, (255, 255, 255), (cx, cy), max(self.raio - 4, 1))
 
 
class Lanca(Projetil):
    COR = (180, 130, 60)
 
    def __init__(self, x, y, alvo_x, alvo_y):
        super().__init__(x, y, alvo_x, alvo_y,
                         velocidade=5, dano=15, cor=self.COR, raio=5, veneno=False)
 
    def desenhar(self, tela, cam_x=0, cam_y=0):
        cx = int(self.rect.centerx - cam_x)
        cy = int(self.rect.centery - cam_y)
        mag = max((self.vx**2 + self.vy**2) ** 0.5, 1)
        nx, ny = self.vx / mag, self.vy / mag
        x1 = int(cx - nx * 10)
        y1 = int(cy - ny * 10)
        x2 = int(cx + nx * 10)
        y2 = int(cy + ny * 10)
        pygame.draw.line(tela, self.COR, (x1, y1), (x2, y2), 3)
        pygame.draw.circle(tela, (220, 220, 180), (x2, y2), 3)

 