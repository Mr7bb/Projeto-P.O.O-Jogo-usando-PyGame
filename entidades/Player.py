import pygame
import os
class Player:
    HP_MAX_BASE = 2000
    DANO_PICARETA = {
        "Fantasma":          3,
        "LegiaoDeFantasmas": 3,
        "CogumeloEsporos":   2,
        "CogumeloAgressivo": 2,
        "Goblin":            3,
        "Slime":             2,
        "Golem":             1,
        "GolemLava":         1,
    }
    DANO_PICARETA_PADRAO = 2  
 
    def __init__(self):
        self.rect       = pygame.Rect(50, 50, 40, 40)
        self.velocidade = 7  # velocidade base 5 -> 7 (pedido pra deixar o player mais rapido)
        self.hp_max     = self.HP_MAX_BASE
        self.hp         = self.hp_max
 
        # status de dot (dano ao longo do tempo). antes o veneno so existia se o
        # esporo acertasse (o atributo nem existia antes disso, dependia de hasattr
        # no Blast_Miner.py pra checar). agora ja nasce zerado, fica mais facil de ler.
        self._veneno_timer = 0
        self._fogo_timer   = 0   # aplicado pelo golpe de solo do Golem de Lava
 
        self.invencivel_timer = 0
        self.bomba_cooldown   = 0
 
        self.direcao_face         = 'baixo'
        self.picareta_cooldown    = 0
        self.picareta_ativa       = False
        self.picareta_timer       = 0
        self.picareta_rect        = None
        self.PICARETA_DURACAO     = 12
        self.PICARETA_COOLDOWN    = 12
        self.PICARETA_ALCANCE     = 55
        
        self.BOMBA_COOLDOWN_BASE  = 240
        self.max_bombas           = 2
        
        self.nivel_forca          = 0
        self.nivel_velocidade     = 0
        self.nivel_hp             = 0
        self.nivel_bomba_alcance  = 0
        self.nivel_bomba_cd       = 0
        self.nivel_bombas_simult  = 0
        self.nivel_escudo         = 0
        
        self.imune_veneno         = False
        self.imune_atordoamento   = False
        self.escudo_cargas        = 0
 
    @property
    def hp_pct(self): return max(0.0, self.hp / self.hp_max)
 
    def controlar(self, paredes, bombas):
        # move um eixo por vez (x depois y) e desfaz o movimento se colidir.
        # fazer separado por eixo evita o bug classico de "grudar" na quina de uma parede
        # quando anda na diagonal.
        pos_antiga_x, pos_antiga_y = self.rect.x, self.rect.y
        teclas = pygame.key.get_pressed()
 
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
        if self.picareta_cooldown > 0: self.picareta_cooldown -= 1
 
        if self.picareta_ativa:
            self.picareta_timer -= 1
            if self.picareta_timer <= 0:
                self.picareta_ativa = False
                self.picareta_rect  = None
 
    def pode_atacar_picareta(self): return self.picareta_cooldown == 0 and not self.picareta_ativa
 
    def atacar(self):
        """Retornado ao formato clássico: Ataca na direção em que o jogador está olhando."""
        if not self.pode_atacar_picareta(): return None
        self.picareta_ativa    = True
        self.picareta_timer    = self.PICARETA_DURACAO
        self.picareta_cooldown = self.PICARETA_COOLDOWN
        self.picareta_rect     = self._calcular_hitbox()
        return self.picareta_rect
 
    def _calcular_hitbox(self):
        al, larg = self.PICARETA_ALCANCE, 50
        cx, cy = self.rect.centerx, self.rect.centery
        if self.direcao_face == 'cima': return pygame.Rect(cx - larg // 2, cy - al - self.rect.height // 2, larg, al)
        elif self.direcao_face == 'baixo': return pygame.Rect(cx - larg // 2, cy + self.rect.height // 2, larg, al)
        elif self.direcao_face == 'esquerda': return pygame.Rect(cx - al - self.rect.width // 2, cy - larg // 2, al, larg)
        else: return pygame.Rect(cx + self.rect.width // 2, cy - larg // 2, al, larg)
 
    def hitbox_picareta_atual(self):
        if self.picareta_ativa and self.picareta_rect: return self._calcular_hitbox()
        return None
 
    def dano_picareta_para(self, inimigo):
        return self.DANO_PICARETA.get(inimigo.__class__.__name__, self.DANO_PICARETA_PADRAO)
 
    def desenhar_picareta(self, tela, cam_x=0, cam_y=0):
        if not self.picareta_ativa or not self.picareta_rect: return
        alpha = int(255 * (self.picareta_timer / self.PICARETA_DURACAO))
        cor = (200, 200, 255)
        r = pygame.Rect(self.picareta_rect.x - cam_x, self.picareta_rect.y - cam_y, self.picareta_rect.width, self.picareta_rect.height)
        surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        surf.fill((*cor, alpha))
        tela.blit(surf, (r.x, r.y))
        pygame.draw.rect(tela, cor, r, 2)
 
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
 
    def pode_plantar_bomba(self): return self.bomba_cooldown == 0
    def plantar_bomba(self): self.bomba_cooldown = self.BOMBA_COOLDOWN_BASE
 
    def aplicar_knockback(self, origem_rect, paredes, bombas):
        dx = 2 if self.rect.centerx - origem_rect.centerx > 0 else -2
        dy = 2 if self.rect.centery - origem_rect.centery > 0 else -2
        for _ in range(40):
            self.rect.x += dx
            for p in paredes:
                if self.rect.colliderect(p): self.rect.x -= dx; dx = 0; break
            for b in bombas:
                if b.solida and self.rect.colliderect(b.rect): self.rect.x -= dx; dx = 0; break
            self.rect.y += dy
            for p in paredes:
                if self.rect.colliderect(p): self.rect.y -= dy; dy = 0; break
            for b in bombas:
                if b.solida and self.rect.colliderect(b.rect): self.rect.y -= dy; dy = 0; break
            if dx == 0 and dy == 0: break

