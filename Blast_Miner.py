import pygame
import random
 
from Mapas.gerador_mapas import GeradorProcedural
from entidades.Player import Player
from entidades.Fantasma import Fantasma, LegiaoDeFantasmas
from entidades.Golem import Golem
from entidades.Cogumelos import CogumeloEsporos, CogumeloAgressivo
from entidades.Goblin import Goblin
from entidades.Slime import Slime
from objetos.Bomba import Bomba
from objetos.Projetil import Esporo, Lanca
from telas.tela_inicial import TelaInicial
from telas.tela_jogo import TelaPause
from telas.tela_gameover import TelaGameOver
 
ALTURA    = 900
LARGURA   = 1200
TELA_SIZE = 50
 
BIOMAS = {
    1: {"parede": (80,  55,  35), "chao": (45, 32, 20),  "pedra": (120, 90,  60), "minerio": (180, 120, 40)},
    2: {"parede": (40,  55,  35), "chao": (25, 35, 20),  "pedra": (70, 100,  55), "minerio": (140,  60, 160)},
    3: {"parede": (50,  60,  90), "chao": (25, 30, 55),  "pedra": (80,  90, 150), "minerio": ( 80, 220, 220)},
    4: {"parede": (30,  20,  20), "chao": (20, 12, 12),  "pedra": (60,  40,  35), "minerio": (220,  80,  20)},
}
 
def _bioma(fase_num):
    if fase_num <= 3: return 1
    if fase_num <= 6: return 2
    if fase_num <= 9: return 3
    return 4
 
def _tabela_spawns(fase_num):
    if fase_num == 1:
        return [(Fantasma, 4, 6)]
    elif fase_num == 2:
        return [(Fantasma, 3, 4), (LegiaoDeFantasmas, 3, 4)]
    elif fase_num == 3:
        return [(CogumeloEsporos, 3, 4), (CogumeloAgressivo, 3, 4)]
    elif fase_num == 4:
        return [(CogumeloEsporos, 2, 3), (CogumeloAgressivo, 2, 3), (Fantasma, 2, 3)]
    elif fase_num == 5:
        return [(Goblin, 4, 5), (Slime, 4, 5)]
    elif fase_num == 6:
        return [(Goblin, 3, 4), (Slime, 3, 4), (Fantasma, 2, 3), (CogumeloEsporos, 2, 3)]
    elif fase_num == 7:
        return [(Golem, 5, 7)]
    elif fase_num == 8:
        return [(Golem, 3, 4), (Fantasma, 3, 4), (Goblin, 3, 4), (Slime, 3, 4)]
    else:
        return [(Golem, 4, 6), (Fantasma, 4, 6), (Goblin, 3, 4),
                (Slime, 3, 4), (CogumeloAgressivo, 2, 3)]
 
 
class BlastMiner:
    def __init__(self):
        pygame.init()
        self.tela  = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Blast Miner Co. - IFRN")
 
        self.clock   = pygame.time.Clock()
        self.gerador = GeradorProcedural()
 
        self.estado        = "menu"
        self.tela_inicial  = TelaInicial(self.tela)
        self.tela_pause    = TelaPause(self.tela)
        self.tela_gameover = TelaGameOver(self.tela)
 
        self.player     = None
        self.fase_atual = 1
        self.mapa       = None
        self.inimigos   = []
        self.paredes    = []
        self.bombas     = []
        self.projeteis  = []  # esporos e lanças voando
        self.saida_rect = None
        self.rodando    = True
 
        self.cam_x = 0
        self.cam_y = 0
 
    # ── setup ──────────────────────────────────────────────
 
    def _resetar_jogo(self):
        self.player     = Player()
        self.fase_atual = 1
        self.paredes    = []
        self.bombas     = []
        self.projeteis  = []
        self.saida_rect = None
        self._carregar_fase(primeiro_spawn=True)
 
    def _carregar_fase(self, primeiro_spawn=False):
        self.bombas    = []
        self.projeteis = []
        self.saida_rect = None
        self.mapa = self.gerador.gerar_fase(self.fase_atual)
 
        if primeiro_spawn:
            self.player.rect.topleft = (TELA_SIZE + 5, TELA_SIZE + 5)
        else:
            livres = self.gerador.listar_chao_livre(self.mapa, excluir_raio=0)
            if livres:
                lin, col = random.choice(livres)
                self.player.rect.topleft = (col * TELA_SIZE + 5, lin * TELA_SIZE + 5)
            else:
                self.player.rect.topleft = (TELA_SIZE + 5, TELA_SIZE + 5)
 
        self._spawnar_inimigos()
 
    def _spawnar_inimigos(self):
        self.inimigos = []
        origem_lin = self.player.rect.centery // TELA_SIZE
        origem_col = self.player.rect.centerx // TELA_SIZE
 
        candidatos = self.gerador.listar_chao_livre(
            self.mapa, excluir_raio=5, origem=(origem_lin, origem_col)
        )
 
        tabela = _tabela_spawns(self.fase_atual)
 
        # BUG CORRIGIDO: legiao_atual criada uma vez por fase
        # e o loop interno estava fora do for — agora está dentro
        legiao_atual = []
 
        for classe, qtd_min, qtd_max in tabela:  # itera cada tipo de mob
            qtd = random.randint(qtd_min, qtd_max)
            posicoes = random.sample(candidatos, min(qtd, len(candidatos)))
 
            for lin, col in posicoes:
                x = col * TELA_SIZE
                y = lin * TELA_SIZE
 
                if classe is LegiaoDeFantasmas:
                    # passa a mesma lista — todos compartilham referência correta
                    mob = LegiaoDeFantasmas(x, y, grupo=legiao_atual)
                    legiao_atual.append(mob)
                else:
                    mob = classe(x, y)
 
                self.inimigos.append(mob)
 
        print(f"[SPAWN] Fase {self.fase_atual}: {len(self.inimigos)} inimigos")
 
    # ── câmera ─────────────────────────────────────────────
 
    def _atualizar_camera(self):
        mapa_largura = self.gerador.colunas * TELA_SIZE
        mapa_altura  = self.gerador.linhas  * TELA_SIZE
 
        self.cam_x = self.player.rect.centerx - LARGURA // 2
        self.cam_y = self.player.rect.centery - ALTURA  // 2
        self.cam_x = max(0, min(self.cam_x, mapa_largura - LARGURA))
        self.cam_y = max(0, min(self.cam_y, mapa_altura  - ALTURA))
 
    # ── lógica ─────────────────────────────────────────────
 
    def _logica_jogo(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.estado = "pause"
                    return
                if event.key == pygame.K_SPACE:
                    if self.player.pode_plantar_bomba() and len(self.bombas) < 1:
                        col = self.player.rect.centerx // TELA_SIZE
                        lin = self.player.rect.centery // TELA_SIZE
                        self.bombas.append(Bomba(col * TELA_SIZE, lin * TELA_SIZE))
                        self.player.plantar_bomba()
 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # clique esquerdo — espada
                    self.player.atacar()
                if event.button == 3:  # clique direito — bomba
                    if self.player.pode_plantar_bomba() and len(self.bombas) < 1:
                        col = self.player.rect.centerx // TELA_SIZE
                        lin = self.player.rect.centery // TELA_SIZE
                        self.bombas.append(Bomba(col * TELA_SIZE, lin * TELA_SIZE))
                        self.player.plantar_bomba()
 
        self.player.controlar(self.paredes, self.bombas)
        if self.player.invencivel_timer > 0:
            self.player.invencivel_timer -= 1
 
        # veneno contínuo
        if hasattr(self.player, '_veneno_timer') and self.player._veneno_timer > 0:
            self.player._veneno_timer -= 1
            if self.player._veneno_timer % 60 == 0:
                self.player.receber_dano(5)
 
        for b in self.bombas[:]:
            b.atualizar(self.mapa, self.player, self.inimigos)
            if b.explodiu:
                self.bombas.remove(b)
 
        # atualiza inimigos e coleta projéteis pendentes
        self.inimigos = [i for i in self.inimigos if i.ativo]
        novos_slimes  = []
        hitbox_espada = self.player.hitbox_espada_atual()
 
        for inimigo in self.inimigos:
            inimigo.mover(self.player, self.paredes, self.mapa, self.bombas)
 
            # coleta projéteis do Cogumelo e do Goblin
            if hasattr(inimigo, 'projeteis_pendentes') and inimigo.projeteis_pendentes:
                for ox, oy, ax, ay in inimigo.projeteis_pendentes:
                    if isinstance(inimigo, CogumeloEsporos):
                        self.projeteis.append(Esporo(ox, oy, ax, ay))
                    elif isinstance(inimigo, Goblin):
                        self.projeteis.append(Lanca(ox, oy, ax, ay))
                inimigo.projeteis_pendentes.clear()
 
            # colisão com espada
            if hitbox_espada and not inimigo._atingindo_esse_swing and inimigo.rect.colliderect(hitbox_espada):
                inimigo._atingindo_esse_swing = True  # evita multi-hit no mesmo swing
                dano = self.player.dano_espada_para(inimigo)
 
                if isinstance(inimigo, Slime):
                    dividiu = inimigo.receber_dano_espada(dano, self.player.rect)
                    if dividiu:
                        # spawna 2 mini-slimes na posição do slime dividido
                        for _ in range(2):
                            mini = Slime(inimigo.rect.x, inimigo.rect.y, mini=True)
                            novos_slimes.append(mini)
                else:
                    inimigo.receber_dano_espada(dano, self.player.rect)
 
            # reseta flag de hit quando a espada para
            if not hitbox_espada:
                inimigo._atingindo_esse_swing = False
 
            if isinstance(inimigo, Golem):
                inimigo.aplicar_knockback_no_player(self.player, self.paredes, self.bombas)
            elif inimigo.rect.colliderect(self.player.rect):
                self.player.receber_dano()
 
        # adiciona mini-slimes gerados por divisão
        for s in novos_slimes:
            self.inimigos.append(s)
 
        # atualiza projéteis voando
        for proj in self.projeteis[:]:
            proj.atualizar(self.player, self.paredes)
            if not proj.ativo:
                self.projeteis.remove(proj)
 
        if self.player.hp <= 0:
            self.estado = "gameover"
            return
 
        if self.saida_rect and self.player.rect.colliderect(self.saida_rect):
            print(f"=== fase {self.fase_atual} -> {self.fase_atual + 1} ===")
            self.fase_atual += 1
            self._carregar_fase(primeiro_spawn=False)
 
        self._atualizar_camera()
 
    # ── desenho ────────────────────────────────────────────
 
    def desenhar_cenario(self):
        self.paredes    = []
        self.saida_rect = None
        cores = BIOMAS[_bioma(self.fase_atual)]
 
        for lin_idx, linha in enumerate(self.mapa):
            for col_idx, tile in enumerate(linha):
                x    = col_idx * TELA_SIZE - self.cam_x
                y    = lin_idx * TELA_SIZE - self.cam_y
                rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
 
                if x + TELA_SIZE < 0 or x > LARGURA or y + TELA_SIZE < 0 or y > ALTURA:
                    rect_mundo = pygame.Rect(col_idx * TELA_SIZE, lin_idx * TELA_SIZE,
                                            TELA_SIZE, TELA_SIZE)
                    if tile in (1, 2, 4):
                        self.paredes.append(rect_mundo)
                    elif tile == 3:
                        self.saida_rect = rect_mundo
                    continue
 
                if tile == 0:
                    pygame.draw.rect(self.tela, cores["chao"], rect)
 
                elif tile == 1:
                    pygame.draw.rect(self.tela, cores["parede"], rect)
                    borda = tuple(min(v + 25, 255) for v in cores["parede"])
                    pygame.draw.rect(self.tela, borda, rect, 2)
                    self.paredes.append(pygame.Rect(col_idx * TELA_SIZE, lin_idx * TELA_SIZE,
                                                    TELA_SIZE, TELA_SIZE))
 
                elif tile == 2:
                    pygame.draw.rect(self.tela, cores["pedra"], rect)
                    pygame.draw.rect(self.tela, cores["chao"], rect, 2)
                    self.paredes.append(pygame.Rect(col_idx * TELA_SIZE, lin_idx * TELA_SIZE,
                                                    TELA_SIZE, TELA_SIZE))
 
                elif tile == 3:
                    self.saida_rect = pygame.Rect(col_idx * TELA_SIZE, lin_idx * TELA_SIZE,
                                                  TELA_SIZE, TELA_SIZE)
                    pygame.draw.rect(self.tela, (20, 20, 20), rect)
                    for degrau in range(3):
                        dy = y + 10 + degrau * 12
                        pygame.draw.rect(self.tela, (200, 160, 80),
                                         pygame.Rect(x + 8 + degrau * 5, dy,
                                                     TELA_SIZE - 16 - degrau * 10, 6))
 
                elif tile == 4:
                    pygame.draw.rect(self.tela, cores["minerio"], rect)
                    inner  = pygame.Rect(x + 10, y + 10, TELA_SIZE - 20, TELA_SIZE - 20)
                    brilho = tuple(min(v + 60, 255) for v in cores["minerio"])
                    pygame.draw.rect(self.tela, brilho, inner)
                    self.paredes.append(pygame.Rect(col_idx * TELA_SIZE, lin_idx * TELA_SIZE,
                                                    TELA_SIZE, TELA_SIZE))
 
    def desenhar_hud(self):
        fonte   = pygame.font.SysFont("monospace", 22, bold=True)
        fonte_p = pygame.font.SysFont("monospace", 16)
 
        barra_x, barra_y   = 10, ALTURA - 50
        barra_larg, barra_alt = 220, 22
 
        pygame.draw.rect(self.tela, (60, 20, 20), (barra_x, barra_y, barra_larg, barra_alt), border_radius=4)
        fill_w = int(barra_larg * self.player.hp_pct)
        if fill_w > 0:
            cor_hp = (int(255 * (1 - self.player.hp_pct)), int(200 * self.player.hp_pct), 30)
            pygame.draw.rect(self.tela, cor_hp, (barra_x, barra_y, fill_w, barra_alt), border_radius=4)
        pygame.draw.rect(self.tela, (200, 200, 200), (barra_x, barra_y, barra_larg, barra_alt), 2, border_radius=4)
        txt_hp = fonte_p.render(f"HP  {self.player.hp}/{self.player.hp_max}", True, (255, 255, 255))
        self.tela.blit(txt_hp, (barra_x + 6, barra_y + 3))
 
        if hasattr(self.player, '_veneno_timer') and self.player._veneno_timer > 0:
            txt_v = fonte_p.render("☠ ENVENENADO", True, (100, 255, 60))
            self.tela.blit(txt_v, (barra_x, barra_y - 20))
 
        if self.player.bomba_cooldown > 0:
            texto_bomba = fonte.render(f"[RMB] BOMBA: {self.player.bomba_cooldown / 60:.1f}s", True, (255, 200, 0))
        else:
            texto_bomba = fonte.render("[RMB] BOMBA: PRONTA", True, (100, 255, 100))
        self.tela.blit(texto_bomba, (250, ALTURA - 45))
 
        # espada
        if self.player.espada_ativa:
            txt_espada = fonte.render("[LMB] ESPADA", True, (255, 230, 80))
        elif self.player.espada_cooldown > 0:
            txt_espada = fonte.render(f"[LMB] {self.player.espada_cooldown / 60:.1f}s", True, (160, 140, 50))
        else:
            txt_espada = fonte.render("[LMB] ESPADA", True, (200, 200, 200))
        self.tela.blit(txt_espada, (530, ALTURA - 45))
 
        nomes = {1: "Minas de Terra", 2: "Caverna de Fungos",
                 3: "Minas de Cristal", 4: "Núcleo Vulcânico"}
        txt_fase = fonte.render(
            f"FASE {self.fase_atual}  |  {nomes[_bioma(self.fase_atual)]}  [{self.gerador.colunas}x{self.gerador.linhas}]",
            True, (180, 180, 180)
        )
        self.tela.blit(txt_fase, (LARGURA // 2 - txt_fase.get_width() // 2, 10))
 
    def _desenhar_jogo(self):
        self.tela.fill((10, 10, 10))
        self.desenhar_cenario()
 
        for b in self.bombas:
            rect_cam = pygame.Rect(b.rect.x - self.cam_x, b.rect.y - self.cam_y,
                                   b.rect.width, b.rect.height)
            pygame.draw.rect(self.tela, b.cor, rect_cam)
 
        # projéteis com offset de câmera
        for proj in self.projeteis:
            proj.desenhar(self.tela, self.cam_x, self.cam_y)
 
        for inimigo in self.inimigos:
            rect_orig = inimigo.rect.copy()
            inimigo.rect = pygame.Rect(inimigo.rect.x - self.cam_x,
                                       inimigo.rect.y - self.cam_y,
                                       inimigo.rect.width, inimigo.rect.height)
            inimigo.desenhar(self.tela)
            inimigo.rect = rect_orig
 
        player_rect_cam = pygame.Rect(self.player.rect.x - self.cam_x,
                                      self.player.rect.y - self.cam_y,
                                      self.player.rect.width, self.player.rect.height)
        if self.player.invencivel_timer % 4 < 2:
            pygame.draw.rect(self.tela, (255, 200, 0), player_rect_cam)
 
        # espada sobre o player
        self.player.desenhar_espada(self.tela, self.cam_x, self.cam_y)
 
        self.desenhar_hud()
 
    # ── loop principal ─────────────────────────────────────
 
    def executar(self):
        while self.rodando:
            events = pygame.event.get()
 
            for event in events:
                if event.type == pygame.QUIT:
                    self.rodando = False
 
                if self.estado == "menu":
                    acao = self.tela_inicial.handle_event(event)
                    if acao == "JOGAR":
                        self._resetar_jogo()
                        self.estado = "jogo"
                    elif acao == "SAIR":
                        self.rodando = False
 
                elif self.estado == "pause":
                    acao = self.tela_pause.handle_event(event)
                    if acao == "CONTINUAR":
                        self.estado = "jogo"
                    elif acao == "MENU PRINCIPAL":
                        self.estado = "menu"
                    elif acao == "SAIR":
                        self.rodando = False
 
                elif self.estado == "gameover":
                    acao = self.tela_gameover.handle_event(event)
                    if acao == "TENTAR NOVAMENTE":
                        self._resetar_jogo()
                        self.estado = "jogo"
                    elif acao == "MENU PRINCIPAL":
                        self.estado = "menu"
                    elif acao == "SAIR":
                        self.rodando = False
 
            if self.estado == "menu":
                self.tela_inicial.draw()
 
            elif self.estado == "jogo":
                self._logica_jogo(events)
                if self.estado == "jogo":
                    self._desenhar_jogo()
                    pygame.display.flip()
 
            elif self.estado == "pause":
                self._desenhar_jogo()
                self.tela_pause.draw()
 
            elif self.estado == "gameover":
                self.tela_gameover.draw()
 
            self.clock.tick(60)
 
        pygame.quit()
 
 
if __name__ == "__main__":
    jogo = BlastMiner()
    jogo.executar()