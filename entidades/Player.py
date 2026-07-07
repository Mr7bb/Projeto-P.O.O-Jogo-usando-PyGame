import pygame
 
class Player:
    HP_MAX_BASE = 100
 
    def __init__(self):
        self.rect = pygame.Rect(50, 50, 40, 40)
        self.velocidade = 5
        self.hp_max = self.HP_MAX_BASE
        self.hp = self.hp_max
        self.invencivel_timer = 0
        self.bomba_cooldown = 0
 
    # hp como porcentagem (0.0 ~ 1.0) pra facilitar desenhar a barra
    @property
    def hp_pct(self):
        return max(0.0, self.hp / self.hp_max)
 
    @property
    def vida(self):
        # compatibilidade com código antigo que checa player.vida <= 0
        return self.hp
 
    def controlar(self, paredes, bombas):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
        teclas = pygame.key.get_pressed()
 
        if teclas[pygame.K_a]: self.rect.x -= self.velocidade
        if teclas[pygame.K_d]: self.rect.x += self.velocidade
        for p in paredes:
            if self.rect.colliderect(p): self.rect.x = pos_antiga_x
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.x = pos_antiga_x
 
        if teclas[pygame.K_w]: self.rect.y -= self.velocidade
        if teclas[pygame.K_s]: self.rect.y += self.velocidade
        for p in paredes:
            if self.rect.colliderect(p): self.rect.y = pos_antiga_y
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.y = pos_antiga_y
 
        if self.bomba_cooldown > 0:
            self.bomba_cooldown -= 1
 
    def pode_plantar_bomba(self):
        return self.bomba_cooldown == 0
 
    def plantar_bomba(self):
        self.bomba_cooldown = 240
 
    def receber_dano(self, quantidade=20):
        if self.invencivel_timer == 0:
            self.hp = max(0, self.hp - quantidade)
            self.invencivel_timer = 60
            print(f"[MIKE] HP: {self.hp}/{self.hp_max}")
 
    def curar(self, quantidade=20):
        self.hp = min(self.hp_max, self.hp + quantidade)
 
    def aumentar_hp_max(self, quantidade=25):
        self.hp_max += quantidade
        self.hp = min(self.hp + quantidade, self.hp_max)
 
    def aplicar_knockback(self, origem_rect, paredes, bombas):
        dx = 2 if self.rect.centerx - origem_rect.centerx > 0 else -1
        dy = 2 if self.rect.centery - origem_rect.centery > 0 else -1
        distancia = 40
 
        for _ in range(distancia):
            self.rect.x += dx
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x -= dx; dx = 0; break
            for b in bombas:
                if b.solida and self.rect.colliderect(b.rect):
                    self.rect.x -= dx; dx = 0; break
 
            self.rect.y += dy
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.y -= dy; dy = 0; break
            for b in bombas:
                if b.solida and self.rect.colliderect(b.rect):
                    self.rect.y -= dy; dy = 0; break
 
            if dx == 0 and dy == 0:
                break 
            