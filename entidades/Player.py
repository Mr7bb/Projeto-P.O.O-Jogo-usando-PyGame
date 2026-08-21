import pygame
import os
 
# carrega as sprites direcionais do player (baseadas na sheet que voce mandou).
# fica cacheado num dict global porque so existe 1 player no jogo, nao precisa
# recarregar a imagem do disco toda vez.
_DIR_SPRITES_PLAYER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
    "sprites",
    "player",
    "mineiro",
)
_SPRITES_PLAYER = {}
_SPRITES_ATAQUE = {}
_SPRITES_DANO = {}
 
def _carregar_sprites_player():
    if _SPRITES_PLAYER:
        return

    def carregar_frames(arquivos):
        return [
            pygame.transform.smoothscale(
                pygame.image.load(os.path.join(_DIR_SPRITES_PLAYER, f'{arquivo}.png')).convert_alpha(),
                (56, 56),
            )
            for arquivo in arquivos
        ]

    try:
        _SPRITES_PLAYER['direita'] = carregar_frames([f'frame_r2_c{coluna}' for coluna in range(1, 5)])
        _SPRITES_PLAYER['esquerda'] = [
            pygame.transform.flip(sprite, True, False)
            for sprite in _SPRITES_PLAYER['direita']
        ]
        _SPRITES_PLAYER['baixo'] = carregar_frames(['frame_r1_c5', 'frame_r2_c5'])
        _SPRITES_PLAYER['cima'] = carregar_frames(['frame_r1_c6', 'frame_r2_c6'])

        _SPRITES_ATAQUE['direita'] = carregar_frames([f'frame_r3_c{coluna}' for coluna in range(1, 5)])
        _SPRITES_ATAQUE['esquerda'] = [
            pygame.transform.flip(sprite, True, False)
            for sprite in _SPRITES_ATAQUE['direita']
        ]
        _SPRITES_ATAQUE['baixo'] = carregar_frames(['frame_r3_c5'])
        _SPRITES_ATAQUE['cima'] = carregar_frames(['frame_r3_c6'])

        _SPRITES_DANO['baixo'] = carregar_frames(['frame_r4_c5'])
        _SPRITES_DANO['cima'] = carregar_frames(['frame_r4_c6'])
        _SPRITES_DANO['esquerda'] = carregar_frames(['frame_r4_c7'])
        _SPRITES_DANO['direita'] = carregar_frames(['frame_r4_c8'])
    except pygame.error as erro:
        _SPRITES_PLAYER.clear()
        _SPRITES_ATAQUE.clear()
        _SPRITES_DANO.clear()
        print(f'[SPRITE PLAYER] nao consegui carregar as sprites: {erro}')
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
        self.rect       = pygame.Rect(40, 40, 40, 40)
        self.velocidade = 4  # velocidade base 5 -> 7 (pedido pra deixar o player mais rapido)
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
        self.sprite_frame         = 0
        self.sprite_timer         = 0
        self.em_movimento         = False
        self.SPRITE_INTERVALO      = 5
        self.picareta_cooldown    = 0
        self.picareta_ativa       = False
        self.picareta_timer       = 0
        self.picareta_rect        = None
        self.PICARETA_DURACAO     = 12
        self.PICARETA_COOLDOWN    = 10
        # alcance 55 -> 75: pedido pra melhorar o alcance da espada/picareta, que
        # tava curto de mais. aumento moderado (nao dobrou), so deu mais margem
        self.PICARETA_ALCANCE     = 75
        
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
 
    def desenhar(self, tela, cam_x=0, cam_y=0):
        _carregar_sprites_player()
        r = pygame.Rect(self.rect.x - cam_x, self.rect.y - cam_y, self.rect.width, self.rect.height)
        sprites = _SPRITES_PLAYER.get(self.direcao_face)
        indice = self.sprite_frame
        deslocamento_y = 0

        # A reacao aparece no comeco da invencibilidade e depois permanece o pisca-pisca.
        if self.invencivel_timer > self.PICARETA_DURACAO * 4:
            sprites = _SPRITES_DANO.get(self.direcao_face)
        elif self.invencivel_timer > 0 and self.invencivel_timer % 4 >= 2:
            return
        elif self.picareta_ativa:
            sprites = _SPRITES_ATAQUE.get(self.direcao_face)
            progresso = self.PICARETA_DURACAO - self.picareta_timer
            indice = progresso * len(sprites) // self.PICARETA_DURACAO if sprites else 0
        elif self.em_movimento:
            deslocamento_y = -1 if self.sprite_frame % 2 else 0

        if sprites:
            sprite = sprites[min(len(sprites) - 1, indice % len(sprites))]
            tela.blit(sprite, sprite.get_rect(center=(r.centerx, r.centery + deslocamento_y)))
        else:
            pygame.draw.rect(tela, (255, 200, 0), r)
    def controlar(self, paredes, bombas, mult_velocidade=1.0):
        # move um eixo por vez (x depois y) e desfaz o movimento se colidir.
        # fazer separado por eixo evita o bug classico de "grudar" na quina de uma parede
        # quando anda na diagonal.
        # mult_velocidade: usado pelo Lodo Corrosivo do boss Gruk (reduz a velocidade
        # enquanto o player pisa na poca). 1.0 = velocidade normal.
        pos_antiga_x, pos_antiga_y = self.rect.x, self.rect.y
        teclas = pygame.key.get_pressed()
        vel = self.velocidade * mult_velocidade
        self.em_movimento = any(teclas[tecla] for tecla in (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s))
 
        if teclas[pygame.K_a]:
            self.rect.x -= vel
            self.direcao_face = 'esquerda'
        if teclas[pygame.K_d]:
            self.rect.x += vel
            self.direcao_face = 'direita'
        for p in paredes:
            if self.rect.colliderect(p): self.rect.x = pos_antiga_x
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.x = pos_antiga_x
 
        if teclas[pygame.K_w]:
            self.rect.y -= vel
            self.direcao_face = 'cima'
        if teclas[pygame.K_s]:
            self.rect.y += vel
            self.direcao_face = 'baixo'
        for p in paredes:
            if self.rect.colliderect(p): self.rect.y = pos_antiga_y
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.y = pos_antiga_y
 
        if self.em_movimento:
            self.sprite_timer += 1
            if self.sprite_timer >= self.SPRITE_INTERVALO:
                self.sprite_timer = 0
                self.sprite_frame += 1
        else:
            self.sprite_frame = 0
            self.sprite_timer = 0

        if self.bomba_cooldown   > 0: self.bomba_cooldown  -= 1
        if self.picareta_cooldown > 0: self.picareta_cooldown -= 1
 
        if self.picareta_ativa:
            self.picareta_timer -= 1
            if self.picareta_timer <= 0:
                self.picareta_ativa = False
                self.picareta_rect  = None
 
    def pode_atacar_picareta(self): return self.picareta_cooldown == 0 and not self.picareta_ativa
 
    def atacar(self):
        """Retornado ao formato clÃƒÆ’Ã‚Â¡ssico: Ataca na direÃƒÆ’Ã‚Â§ÃƒÆ’Ã‚Â£o em que o jogador estÃƒÆ’Ã‚Â¡ olhando."""
        if not self.pode_atacar_picareta(): return None
        self.picareta_ativa    = True
        self.picareta_timer    = self.PICARETA_DURACAO
        self.picareta_cooldown = self.PICARETA_COOLDOWN
        self.picareta_rect     = self._calcular_hitbox()
        return self.picareta_rect
 
    def _calcular_hitbox(self):
        al, larg = self.PICARETA_ALCANCE, 58  # largura 50 -> 58, acompanha o aumento de alcance
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