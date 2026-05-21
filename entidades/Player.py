import pygame

class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, 50, 40, 40)
        self.velocidade = 5
        self.vida = 3
        self.invencivel_timer = 0
        self.bomba_cooldown = 0

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

    def receber_dano(self):
        if self.invencivel_timer == 0:
            self.vida -= 1
            self.invencivel_timer = 60
            print(f"[MIKE] Recebeu dano! Vida: {self.vida}")

    def aplicar_knockback(self, origem_rect, paredes, bombas):
        """Empurra o player para longe de uma origem, respeitando colisões."""
        dx = 2 if self.rect.centerx - origem_rect.centerx > 0 else -1
        dy = 2 if self.rect.centery - origem_rect.centery > 0 else -1
        distancia = 40

        for _ in range(distancia):
            self.rect.x += dx
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x -= dx
                    dx = 0
                    break
            for b in bombas:
                if b.solida and self.rect.colliderect(b.rect):
                    self.rect.x -= dx
                    dx = 0
                    break

            self.rect.y += dy
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.y -= dy
                    dy = 0
                    break
            for b in bombas:
                if b.solida and self.rect.colliderect(b.rect):
                    self.rect.y -= dy
                    dy = 0
                    break

            if dx == 0 and dy == 0:
                break