import pygame
import random

from Mapas.gerador_mapas import GeradorProcedural
from entidades.Player import Player
from entidades.Fantasma import Fantasma, LegiaoDeFantasmas
from entidades.Golem import Golem
from entidades.Cogumelos import CogumeloEsporos, CogumeloAgressivo
from entidades.Goblin import Goblin
from entidades.Slime import Slime
from entidades.NPC import NPC
from objetos.Bomba import Bomba
from objetos.Projetil import Esporo, Lanca
from objetos.Inventario import Inventario
from objetos.Drops import gerar_drops_mob
from telas.tela_inicial import TelaInicial
from telas.tela_jogo import TelaPause
from telas.tela_gameover import TelaGameOver
from telas.tela_loja import TelaLoja

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
        self.tela   = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Blast Miner Co. - IFRN")
        self.clock  = pygame.time.Clock()
        self.gerador = GeradorProcedural()

        self.estado        = "menu"
        self.tela_inicial  = TelaInicial(self.tela)
        self.tela_pause    = TelaPause(self.tela)
        self.tela_gameover = TelaGameOver(self.tela)
        self.tela_loja     = TelaLoja(self.tela)

        self.player     = None
        self.inventario = None
        self.fase_atual = 1
        self.mapa       = None
        self.inimigos   = []
        self.paredes    = []
        self.bombas     = []
        self.projeteis  = []
        self.itens_chao = []
        self.npcs       = []
        self.saida_rect = None
        self.saida_aberta = False
        self.rodando    = True
        self.cam_x      = 0
        self.cam_y      = 0

    # ── setup ──────────────────────────────────────────────

    def _resetar_jogo(self):
        self.player     = Player()
        self.inventario = Inventario()
        self.fase_atual = 1
        self._carregar_fase(primeiro_spawn=True)

    def _carregar_fase(self, primeiro_spawn=False):
        self.bombas       = []
        self.projeteis    = []
        self.itens_chao   = []
        self.npcs         = []
        self.saida_rect   = None
        self.saida_aberta = False
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

        legiao_atual = []
        for classe, qtd_min, qtd_max in _tabela_spawns(self.fase_atual):
            qtd = random.randint(qtd_min, qtd_max)
            posicoes = random.sample(candidatos, min(qtd, len(candidatos)))
            for lin, col in posicoes:
                x = col * TELA_SIZE
                y = lin * TELA_SIZE
                if classe is LegiaoDeFantasmas:
                    mob = LegiaoDeFantasmas(x, y, grupo=legiao_atual)
                    legiao_atual.append(mob)
                else:
                    mob = classe(x, y)
                self.inimigos.append(mob)

    def _spawnar_npcs(self):
        if not self.saida_rect:
            return
        sc = self.saida_rect.x // TELA_SIZE
        sl = self.saida_rect.y // TELA_SIZE
        # ferreiro à esquerda da saída, ambulante à direita
        self.npcs = [
            NPC((sc - 2) * TELA_SIZE, sl * TELA_SIZE, "ferreiro"),
            NPC((sc + 2) * TELA_SIZE, sl * TELA_SIZE, "ambulante"),
        ]

    # ── câmera ─────────────────────────────────────────────

    def _atualizar_camera(self):
        mapa_larg = self.gerador.colunas * TELA_SIZE
        mapa_alt  = self.gerador.linhas  * TELA_SIZE
        self.cam_x = max(0, min(self.player.rect.centerx - LARGURA // 2, mapa_larg - LARGURA))
        self.cam_y = max(0, min(self.player.rect.centery - ALTURA  // 2, mapa_alt  - ALTURA))

    # ── lógica ─────────────────────────────────────────────

    def _logica_jogo(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.estado = "pause"
                    return
                if event.key == pygame.K_e:
                    self._tentar_interagir_npc()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.player.atacar()
                if event.button == 3:
                    qtd_bombas = len(self.bombas)
                    if self.player.pode_plantar_bomba() and qtd_bombas < self.player.max_bombas:
                        col = self.player.rect.centerx // TELA_SIZE
                        lin = self.player.rect.centery // TELA_SIZE
                        alcance_extra = self.player.nivel_bomba_alcance
                        self.bombas.append(Bomba(col * TELA_SIZE, lin * TELA_SIZE, alcance_extra))
                        self.player.plantar_bomba()

        # loja aberta — não processa jogo
        if self.tela_loja.visivel:
            return

        self.player.controlar(self.paredes, self.bombas)
        if self.player.invencivel_timer > 0:
            self.player.invencivel_timer -= 1

        # veneno
        if not self.player.imune_veneno:
            if hasattr(self.player, '_veneno_timer') and self.player._veneno_timer > 0:
                self.player._veneno_timer -= 1
                if self.player._veneno_timer % 60 == 0:
                    self.player.receber_dano(5)

        # bombas
        for b in self.bombas[:]:
            b.atualizar(self.mapa, self.player, self.inimigos)
            if b.drops_gerados:
                self.itens_chao.extend(b.drops_gerados)
                b.drops_gerados.clear()
            if b.explodiu:
                self.bombas.remove(b)

        # inimigos
        self.inimigos   = [i for i in self.inimigos if i.ativo]
        novos_slimes    = []
        hitbox_espada   = self.player.hitbox_espada_atual()

        for inimigo in self.inimigos:
            inimigo.mover(self.player, self.paredes, self.mapa, self.bombas)

            if hasattr(inimigo, 'projeteis_pendentes') and inimigo.projeteis_pendentes:
                for ox, oy, ax, ay in inimigo.projeteis_pendentes:
                    if isinstance(inimigo, CogumeloEsporos):
                        self.projeteis.append(Esporo(ox, oy, ax, ay))
                    elif isinstance(inimigo, Goblin):
                        self.projeteis.append(Lanca(ox, oy, ax, ay))
                inimigo.projeteis_pendentes.clear()

            if hitbox_espada and not inimigo._atingindo_esse_swing and inimigo.rect.colliderect(hitbox_espada):
                inimigo._atingindo_esse_swing = True
                dano = self.player.dano_espada_para(inimigo)
                if isinstance(inimigo, Slime):
                    dividiu = inimigo.receber_dano_espada(dano, self.player.rect)
                    if dividiu:
                        for _ in range(2):
                            novos_slimes.append(Slime(inimigo.rect.x, inimigo.rect.y, mini=True))
                else:
                    inimigo.receber_dano_espada(dano, self.player.rect)

            if not hitbox_espada:
                inimigo._atingindo_esse_swing = False

            # drops ao morrer
            if not inimigo.ativo:
                drops = gerar_drops_mob(inimigo)
                self.itens_chao.extend(drops)

            if isinstance(inimigo, Golem):
                inimigo.aplicar_knockback_no_player(self.player, self.paredes, self.bombas)
            elif inimigo.rect.colliderect(self.player.rect):
                self.player.receber_dano()

        for s in novos_slimes:
            self.inimigos.append(s)

        # projéteis
        for proj in self.projeteis[:]:
            proj.atualizar(self.player, self.paredes)
            if not proj.ativo:
                self.projeteis.remove(proj)

        # itens no chão
        for item in self.itens_chao[:]:
            tipo_coletado = item.atualizar(self.player)
            if tipo_coletado:
                self.inventario.adicionar(tipo_coletado)
                self.itens_chao.remove(item)

        # alçapão — abre quando não tem mais inimigos
        if not self.saida_aberta and len(self.inimigos) == 0:
            self.saida_aberta = True
            self._spawnar_npcs()

        # colisão com saída (só quando aberta e sem loja aberta)
        if self.saida_aberta and not self.tela_loja.visivel:
            if self.saida_rect and self.player.rect.colliderect(self.saida_rect):
                self.fase_atual += 1
                self._carregar_fase(primeiro_spawn=False)
                return

        if self.player.hp <= 0:
            self.estado = "gameover"
            return

        self._atualizar_camera()

    def _tentar_interagir_npc(self):
        for npc in self.npcs:
            if npc.perto_do_player(self.player):
                self.tela_loja.abrir(npc.tipo)
                return

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
                rect_mundo = pygame.Rect(col_idx * TELA_SIZE, lin_idx * TELA_SIZE, TELA_SIZE, TELA_SIZE)

                if x + TELA_SIZE < 0 or x > LARGURA or y + TELA_SIZE < 0 or y > ALTURA:
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
                    self.paredes.append(rect_mundo)

                elif tile == 2:
                    pygame.draw.rect(self.tela, cores["pedra"], rect)
                    pygame.draw.rect(self.tela, cores["chao"], rect, 2)
                    self.paredes.append(rect_mundo)

                elif tile == 3:
                    self.saida_rect = rect_mundo
                    if self.saida_aberta:
                        # aberta: escada normal
                        pygame.draw.rect(self.tela, (20, 20, 20), rect)
                        for degrau in range(3):
                            dy = y + 10 + degrau * 12
                            pygame.draw.rect(self.tela, (200, 160, 80),
                                             pygame.Rect(x + 8 + degrau*5, dy,
                                                         TELA_SIZE - 16 - degrau*10, 6))
                    else:
                        # fechada: alçapão vermelho com cadeado
                        pygame.draw.rect(self.tela, (80, 20, 20), rect)
                        pygame.draw.rect(self.tela, (180, 40, 40), rect, 3)
                        fonte_c = pygame.font.SysFont("monospace", 22, bold=True)
                        cad = fonte_c.render("🔒", True, (255, 80, 80))
                        self.tela.blit(cad, (x + TELA_SIZE//2 - cad.get_width()//2,
                                             y + TELA_SIZE//2 - cad.get_height()//2))

                elif tile == 4:
                    pygame.draw.rect(self.tela, cores["minerio"], rect)
                    inner  = pygame.Rect(x + 10, y + 10, TELA_SIZE - 20, TELA_SIZE - 20)
                    brilho = tuple(min(v + 60, 255) for v in cores["minerio"])
                    pygame.draw.rect(self.tela, brilho, inner)
                    self.paredes.append(rect_mundo)

    def desenhar_hud(self):
        fonte   = pygame.font.SysFont("monospace", 20, bold=True)
        fonte_p = pygame.font.SysFont("monospace", 15)
        fonte_s = pygame.font.SysFont("monospace", 13)

        # ── barra de HP ──────────────────────────────────
        bx, by = 10, ALTURA - 50
        bl, ba = 220, 22
        pygame.draw.rect(self.tela, (60, 20, 20), (bx, by, bl, ba), border_radius=4)
        fw = int(bl * self.player.hp_pct)
        if fw > 0:
            cor_hp = (int(255*(1-self.player.hp_pct)), int(200*self.player.hp_pct), 30)
            pygame.draw.rect(self.tela, cor_hp, (bx, by, fw, ba), border_radius=4)
        pygame.draw.rect(self.tela, (200, 200, 200), (bx, by, bl, ba), 2, border_radius=4)
        txt_hp = fonte_p.render(f"HP  {self.player.hp}/{self.player.hp_max}", True, (255, 255, 255))
        self.tela.blit(txt_hp, (bx + 6, by + 3))

        if not self.player.imune_veneno and hasattr(self.player, '_veneno_timer') and self.player._veneno_timer > 0:
            self.tela.blit(fonte_p.render("☠ ENVENENADO", True, (100, 255, 60)), (bx, by - 20))

        # ── bomba ─────────────────────────────────────────
        if self.player.bomba_cooldown > 0:
            tb = fonte.render(f"[RMB] {self.player.bomba_cooldown/60:.1f}s", True, (255, 200, 0))
        else:
            tb = fonte.render("[RMB] BOMBA", True, (100, 255, 100))
        self.tela.blit(tb, (250, ALTURA - 45))

        # ── espada ────────────────────────────────────────
        if self.player.espada_ativa:
            te = fonte.render("[LMB] ESPADA", True, (255, 230, 80))
        elif self.player.espada_cooldown > 0:
            te = fonte.render(f"[LMB] {self.player.espada_cooldown/60:.1f}s", True, (160, 140, 50))
        else:
            te = fonte.render("[LMB] ESPADA", True, (200, 200, 200))
        self.tela.blit(te, (470, ALTURA - 45))

        # ── fase ──────────────────────────────────────────
        nomes = {1:"Minas de Terra", 2:"Caverna de Fungos", 3:"Minas de Cristal", 4:"Núcleo Vulcânico"}
        tf = fonte.render(
            f"FASE {self.fase_atual}  |  {nomes[_bioma(self.fase_atual)]}  [{self.gerador.colunas}x{self.gerador.linhas}]",
            True, (180, 180, 180)
        )
        self.tela.blit(tf, (LARGURA//2 - tf.get_width()//2, 10))

        # ── saída aberta ──────────────────────────────────
        if self.saida_aberta:
            msg = fonte.render("✔ SAÍDA ABERTA — aperte E para comprar upgrades!", True, (80, 255, 120))
            self.tela.blit(msg, (LARGURA//2 - msg.get_width()//2, 40))

        # ── inimigos restantes ────────────────────────────
        vivos = len(self.inimigos)
        cor_v = (255, 100, 100) if vivos > 0 else (100, 255, 100)
        tv = fonte_p.render(f"Inimigos: {vivos}", True, cor_v)
        self.tela.blit(tv, (LARGURA - tv.get_width() - 10, 10))

        # ── barra lateral de status/upgrades ─────────────
        self._desenhar_barra_status()

        # ── inventário compacto (canto superior esquerdo) ─
        self._desenhar_inventario_hud()

    def _desenhar_barra_status(self):
        fonte = pygame.font.SysFont("monospace", 15, bold=True)
        p = self.player
        items = [
            ("⚔", "Força",    p.nivel_forca,         5),
            ("💨", "Vel",      p.nivel_velocidade,    4),
            ("❤", "Vida",     p.nivel_hp,            5),
            ("💣", "Bomba",    p.nivel_bomba_alcance, 3),
            ("⏱", "Pavio",    p.nivel_bomba_cd,      3),
        ]
        sx, sy = 10, 60
        for icone, label, nivel, maximo in items:
            txt = fonte.render(f"{icone} {label}: {'■'*nivel}{'□'*(maximo-nivel)}", True, (200, 200, 255))
            self.tela.blit(txt, (sx, sy))
            sy += 22

    def _desenhar_inventario_hud(self):
        fonte = pygame.font.SysFont("monospace", 13)
        ix, iy = LARGURA - 180, 35
        pygame.draw.rect(self.tela, (15, 15, 30, 180), (ix - 5, iy - 5, 175, 190))
        pygame.draw.rect(self.tela, (60, 60, 100), (ix - 5, iy - 5, 175, 190), 1)

        titulo = pygame.font.SysFont("monospace", 13, bold=True).render("INVENTÁRIO", True, (180, 180, 255))
        self.tela.blit(titulo, (ix, iy))
        iy += 18

        for nome, qtd in self.inventario.itens.items():
            if qtd > 0:
                cor = (180, 220, 180) if qtd > 0 else (100, 100, 100)
                t = fonte.render(f"{nome[:14]:<14} {qtd}", True, cor)
                self.tela.blit(t, (ix, iy))
                iy += 15
                if iy > ALTURA - 100:
                    break

    # ── prompt de NPC ──────────────────────────────────────

    def _desenhar_prompt_npc(self):
        for npc in self.npcs:
            if npc.perto_do_player(self.player):
                fonte = pygame.font.SysFont("monospace", 16, bold=True)
                rx = npc.rect.x - self.cam_x
                ry = npc.rect.y - self.cam_y - 30
                txt = fonte.render(f"[E] {npc.nome}", True, (255, 255, 100))
                self.tela.blit(txt, (rx - txt.get_width()//2 + 20, ry))

    def _desenhar_jogo(self):
        self.tela.fill((10, 10, 10))
        self.desenhar_cenario()

        for b in self.bombas:
            rc = pygame.Rect(b.rect.x - self.cam_x, b.rect.y - self.cam_y, b.rect.width, b.rect.height)
            pygame.draw.rect(self.tela, b.cor, rc)

        for item in self.itens_chao:
            item.desenhar(self.tela, self.cam_x, self.cam_y)

        for proj in self.projeteis:
            proj.desenhar(self.tela, self.cam_x, self.cam_y)

        for npc in self.npcs:
            npc.desenhar(self.tela, self.cam_x, self.cam_y)

        for inimigo in self.inimigos:
            ro = inimigo.rect.copy()
            inimigo.rect = pygame.Rect(inimigo.rect.x - self.cam_x, inimigo.rect.y - self.cam_y,
                                       inimigo.rect.width, inimigo.rect.height)
            inimigo.desenhar(self.tela)
            inimigo.rect = ro

        pr = pygame.Rect(self.player.rect.x - self.cam_x, self.player.rect.y - self.cam_y,
                         self.player.rect.width, self.player.rect.height)
        if self.player.invencivel_timer % 4 < 2:
            pygame.draw.rect(self.tela, (255, 200, 0), pr)

        self.player.desenhar_espada(self.tela, self.cam_x, self.cam_y)

        self._desenhar_prompt_npc()
        self.desenhar_hud()

    # ── loop principal ─────────────────────────────────────

    def executar(self):
        while self.rodando:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.rodando = False

                if self.tela_loja.visivel:
                    self.tela_loja.handle_event(event, self.inventario, self.player)
                    continue

                if self.estado == "menu":
                    acao = self.tela_inicial.handle_event(event)
                    if acao == "JOGAR":
                        self._resetar_jogo()
                        self.estado = "jogo"
                    elif acao == "SAIR":
                        self.rodando = False

                elif self.estado == "pause":
                    acao = self.tela_pause.handle_event(event)
                    if acao == "CONTINUAR": self.estado = "jogo"
                    elif acao == "MENU PRINCIPAL": self.estado = "menu"
                    elif acao == "SAIR": self.rodando = False

                elif self.estado == "gameover":
                    acao = self.tela_gameover.handle_event(event)
                    if acao == "TENTAR NOVAMENTE":
                        self._resetar_jogo()
                        self.estado = "jogo"
                    elif acao == "MENU PRINCIPAL": self.estado = "menu"
                    elif acao == "SAIR": self.rodando = False

            if self.estado == "menu":
                self.tela_inicial.draw()
            elif self.estado == "jogo":
                self._logica_jogo(events)
                if self.estado == "jogo":
                    self._desenhar_jogo()
                    if self.tela_loja.visivel:
                        self.tela_loja.draw(self.inventario, self.player)
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