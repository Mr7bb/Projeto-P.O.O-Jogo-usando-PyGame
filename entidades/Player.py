import pygame

class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, 50, 40, 40)  # 40x40 para não entalar nas paredes
        self.velocidade = 5
        self.vida = 3
        self.invencivel_timer = 0
        self.bomba_cooldown = 0       # Cooldown entre bombas (240 frames = 4 segundos)

    def controlar(self, paredes, bombas):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
        teclas = pygame.key.get_pressed()

        # Movimento X
        if teclas[pygame.K_a]: self.rect.x -= self.velocidade
        if teclas[pygame.K_d]: self.rect.x += self.velocidade
        for p in paredes:
            if self.rect.colliderect(p): self.rect.x = pos_antiga_x
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.x = pos_antiga_x

        # Movimento Y
        if teclas[pygame.K_w]: self.rect.y -= self.velocidade
        if teclas[pygame.K_s]: self.rect.y += self.velocidade
        for p in paredes:
            if self.rect.colliderect(p): self.rect.y = pos_antiga_y
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.y = pos_antiga_y

        # Atualiza cooldown da bomba
        if self.bomba_cooldown > 0:
            self.bomba_cooldown -= 1

    def pode_plantar_bomba(self):
        return self.bomba_cooldown == 0

    def plantar_bomba(self):
        self.bomba_cooldown = 240  # 4 segundos a 60fps

    def receber_dano(self):
        if self.invencivel_timer == 0:
            self.vida -= 1
            self.invencivel_timer = 60  # 1 segundo de proteção
            print(f"[MIKE] Recebeu dano! Vida: {self.vida}")

    def aplicar_knockback(self, origem_rect):
        """Empurra o player para longe de uma origem (usado pelo Golem)."""
        dx = self.rect.centerx - origem_rect.centerx
        dy = self.rect.centery - origem_rect.centery
        if dx != 0: self.rect.x += 40 * (1 if dx > 0 else -1)
        if dy != 0: self.rect.y += 40 * (1 if dy > 0 else -1)
