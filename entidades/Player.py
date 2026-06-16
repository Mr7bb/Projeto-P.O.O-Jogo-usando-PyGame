import pygame
import math

class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, 50, 40, 40)
        self.velocidade = 5
        self.vida = 3
        self.invencivel_timer = 0
        self.bomba_cooldown = 0

        self.direcao = "direita"

        self.ataque_timer    = 0
        self.ataque_cooldown = 0
        self.rect_ataque     = None

        self.ATAQUE_DURACAO  = 14
        self.ATAQUE_COOLDOWN = 35
        self.ATAQUE_DANO     = 1
        self.ESPADA_COMP     = 38
        self.ESPADA_LARG     = 10

        self._ARCOS = {
            "direita":   (-60,  60),
            "esquerda":  (120, 240),
            "cima":      (-150, -30),
            "baixo":     (30,  150),
        }

        self._cor_espada    = (200, 210, 220)
        self._cor_impacto   = (255, 180,  50)
        self._frame_impacto = 0

    def controlar(self, paredes, bombas):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_a]:
            self.rect.x -= self.velocidade
            self.direcao = "esquerda"
        if teclas[pygame.K_d]:
            self.rect.x += self.velocidade
            self.direcao = "direita"
        for p in paredes:
            if self.rect.colliderect(p): self.rect.x = pos_antiga_x
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.x = pos_antiga_x

        if teclas[pygame.K_w]:
            self.rect.y -= self.velocidade
            self.direcao = "cima"
        if teclas[pygame.K_s]:
            self.rect.y += self.velocidade
            self.direcao = "baixo"
        for p in paredes:
            if self.rect.colliderect(p): self.rect.y = pos_antiga_y
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.y = pos_antiga_y

        if self.bomba_cooldown  > 0: self.bomba_cooldown  -= 1
        if self.ataque_cooldown > 0: self.ataque_cooldown -= 1
        if self._frame_impacto  > 0: self._frame_impacto  -= 1

        if self.ataque_timer > 0:
            self.ataque_timer -= 1
            self._atualizar_hitbox()
        else:
            self.rect_ataque = None

    def pode_plantar_bomba(self):
        return self.bomba_cooldown == 0

    def plantar_bomba(self):
        self.bomba_cooldown = 240

    def pode_atacar(self):
        return self.ataque_cooldown == 0

    def iniciar_ataque(self):
        self.ataque_timer    = self.ATAQUE_DURACAO
        self.ataque_cooldown = self.ATAQUE_COOLDOWN
        self._atualizar_hitbox()

    def flash_impacto(self):
        self._frame_impacto = 6

    def _angulo_atual(self):
        ang_ini, ang_fim = self._ARCOS[self.direcao]
        progresso = 1.0 - (self.ataque_timer / self.ATAQUE_DURACAO)
        return ang_ini + (ang_fim - ang_ini) * progresso

    def _atualizar_hitbox(self):
        ang = math.radians(self._angulo_atual())
        cx, cy = self.rect.centerx, self.rect.centery
        raio_base = 22
        ponta_x = cx + math.cos(ang) * (raio_base + self.ESPADA_COMP)
        ponta_y = cy + math.sin(ang) * (raio_base + self.ESPADA_COMP)
        hw = 18
        self.rect_ataque = pygame.Rect(int(ponta_x) - hw, int(ponta_y) - hw, hw*2, hw*2)

    def desenhar_espada(self, tela):
        if self.ataque_timer <= 0:
            return

        ang = math.radians(self._angulo_atual())
        cx, cy = self.rect.centerx, self.rect.centery
        raio_base = 22

        base_x  = cx + math.cos(ang) * raio_base
        base_y  = cy + math.sin(ang) * raio_base
        ponta_x = cx + math.cos(ang) * (raio_base + self.ESPADA_COMP)
        ponta_y = cy + math.sin(ang) * (raio_base + self.ESPADA_COMP)

        cor = self._cor_impacto if self._frame_impacto > 0 else self._cor_espada

        pygame.draw.line(tela, cor,
                         (int(base_x), int(base_y)),
                         (int(ponta_x), int(ponta_y)), self.ESPADA_LARG)
        pygame.draw.line(tela, (240, 245, 255),
                         (int(base_x), int(base_y)),
                         (int(ponta_x), int(ponta_y)), 3)
        perp = ang + math.pi / 2
        gx, gy = math.cos(perp) * 7, math.sin(perp) * 7
        pygame.draw.line(tela, (160, 130, 60),
                         (int(base_x - gx), int(base_y - gy)),
                         (int(base_x + gx), int(base_y + gy)), 5)
        pygame.draw.circle(tela, cor, (int(ponta_x), int(ponta_y)), 4)

    def receber_dano(self):
        if self.invencivel_timer == 0:
            self.vida -= 1
            self.invencivel_timer = 60
            print(f"[MIKE] Recebeu dano! Vida: {self.vida}")

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