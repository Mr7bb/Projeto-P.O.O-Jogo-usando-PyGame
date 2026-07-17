import pygame
import math

class Player:
    HP_MAX_BASE = 100

    # dano base da espada por tipo de mob (nome da classe)
    DANO_ESPADA = {
        "Fantasma":          3,
        "LegiaoDeFantasmas": 3,
        "CogumeloEsporos":   2,
        "CogumeloAgressivo": 2,
        "Goblin":            3,
        "Slime":             2,
        "Golem":             1,
    }
    DANO_ESPADA_PADRAO = 2  # fallback pra qualquer outro mob

    def __init__(self):
        self.rect       = pygame.Rect(50, 50, 40, 40)
        self.velocidade = 5
        self.hp_max     = self.HP_MAX_BASE
        self.hp         = self.hp_max

        self.invencivel_timer = 0
        self.bomba_cooldown   = 0

        # espada
        self.direcao_face         = 'baixo'
        self.espada_cooldown      = 0
        self.espada_ativa         = False
        self.espada_timer         = 0
        self.espada_rect          = None
        self.ESPADA_DURACAO       = 12
        self.ESPADA_COOLDOWN      = 30
        self.ESPADA_ALCANCE       = 55
        # bomba
        self.BOMBA_COOLDOWN_BASE  = 240
        self.max_bombas           = 1
        # níveis de upgrade
        self.nivel_forca          = 0
        self.nivel_velocidade     = 0
        self.nivel_hp             = 0
        self.nivel_bomba_alcance  = 0
        self.nivel_bomba_cd       = 0
        self.nivel_bombas_simult  = 0
        self.nivel_escudo         = 0
        # status especiais
        self.imune_veneno         = False
        self.imune_atordoamento   = False
        self.escudo_cargas        = 0

    @property
    def hp_pct(self):
        return max(0.0, self.hp / self.hp_max)

    @property
    def vida(self):
        return self.hp

    # ── movimento ──────────────────────────────────────────

    def controlar(self, paredes, bombas):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
        teclas = pygame.key.get_pressed()

        # atualiza direção face com base no movimento
        if teclas[pygame.K_a]:
            self.rect.x -= self.velocidade
            self.direcao_face = 'esquerda'
        if teclas[pygame.K_d]:
            self.rect.x += self.velocidade
            self.direcao_face = 'direita'
        for p in paredes:
            if self.rect.colliderect(p): self.rect.x = pos_antiga_x
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.x = pos_antiga_x

        if teclas[pygame.K_w]:
            self.rect.y -= self.velocidade
            self.direcao_face = 'cima'
        if teclas[pygame.K_s]:
            self.rect.y += self.velocidade
            self.direcao_face = 'baixo'
        for p in paredes:
            if self.rect.colliderect(p): self.rect.y = pos_antiga_y
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.y = pos_antiga_y

        if self.bomba_cooldown   > 0: self.bomba_cooldown  -= 1
        if self.espada_cooldown  > 0: self.espada_cooldown -= 1

        # atualiza timer da hitbox ativa
        if self.espada_ativa:
            self.espada_timer -= 1
            if self.espada_timer <= 0:
                self.espada_ativa = False
                self.espada_rect  = None

    # ── espada ─────────────────────────────────────────────

    def pode_atacar_espada(self):
        return self.espada_cooldown == 0 and not self.espada_ativa

    def atacar(self):
        """Inicia o swing. Retorna o rect da hitbox ou None."""
        if not self.pode_atacar_espada():
            return None

        self.espada_ativa    = True
        self.espada_timer    = self.ESPADA_DURACAO
        self.espada_cooldown = self.ESPADA_COOLDOWN
        self.espada_rect     = self._calcular_hitbox()
        return self.espada_rect

    def _calcular_hitbox(self):
        """Rect retangular à frente do player na direção face."""
        al = self.ESPADA_ALCANCE
        larg, alt = 50, 30   # dimensões da hitbox perpendicular

        cx, cy = self.rect.centerx, self.rect.centery

        if self.direcao_face == 'cima':
            return pygame.Rect(cx - larg // 2, cy - al - self.rect.height // 2, larg, al)
        elif self.direcao_face == 'baixo':
            return pygame.Rect(cx - larg // 2, cy + self.rect.height // 2, larg, al)
        elif self.direcao_face == 'esquerda':
            return pygame.Rect(cx - al - self.rect.width // 2, cy - larg // 2, al, larg)
        else:  # direita
            return pygame.Rect(cx + self.rect.width // 2, cy - larg // 2, al, larg)

    def hitbox_espada_atual(self):
        """Retorna a hitbox se estiver ativa, senão None."""
        if self.espada_ativa and self.espada_rect:
            return self._calcular_hitbox()  # recalcula pra seguir o player
        return None

    def dano_espada_para(self, inimigo):
        nome = inimigo.__class__.__name__
        return self.DANO_ESPADA.get(nome, self.DANO_ESPADA_PADRAO)

    def desenhar_espada(self, tela, cam_x=0, cam_y=0):
        """Desenha o arco visual da espada enquanto ativa."""
        if not self.espada_ativa or not self.espada_rect:
            return

        # opacidade diminui conforme o timer cai
        alpha = int(255 * (self.espada_timer / self.ESPADA_DURACAO))
        cor   = (255, 230, 80)

        # rect com offset da câmera
        r = pygame.Rect(
            self.espada_rect.x - cam_x,
            self.espada_rect.y - cam_y,
            self.espada_rect.width,
            self.espada_rect.height
        )

        # surface semitransparente
        surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        surf.fill((*cor, alpha))
        tela.blit(surf, (r.x, r.y))

        # borda sólida
        pygame.draw.rect(tela, cor, r, 2)

    # ── dano / cura ────────────────────────────────────────

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

    def pode_plantar_bomba(self):
        return self.bomba_cooldown == 0

    def plantar_bomba(self):
        self.bomba_cooldown = self.BOMBA_COOLDOWN_BASE

    def aplicar_knockback(self, origem_rect, paredes, bombas):
        dx = 2 if self.rect.centerx - origem_rect.centerx > 0 else -2
        dy = 2 if self.rect.centery - origem_rect.centery > 0 else -2

        for _ in range(40):
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