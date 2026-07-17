import pygame
import random

from Mapas.gerador_mapas import GeradorProcedural
from entidades.Player import Player
from entidades.Fantasma import Fantasma, LegiaoDeFantasmas
from entidades.Golem import Golem
from entidades.Cogumelos import CogumeloEsporos, CogumeloAgressivo
from entidades.Goblin import Goblin
from entidades.Slime import Slime
from entidades.vendedor import vendedor, ambulante
from objetos.Bomba import Bomba
from objetos.Projetil import Esporo, Lanca
from objetos.Inventario import Inventario
from objetos.Drops import gerar_drops_mob

from telas.tela_inicial import TelaInicial
from telas.tela_jogo import TelaPause
from telas.tela_gameover import TelaGameOver
from telas.tela_loja import TelaLoja

# Máquina de estados imports
from telas.tela_estado_game import TransicaoFade
from telas.telas_estado_jogo import EstadoJogando
from telas.tela_estado_adaptadores import EstadoMenuAdaptador, EstadoPauseAdaptador, EstadoGameOverAdaptador, EstadoLojaAdaptador

ALTURA    = 900
LARGURA   = 1200
TELA_SIZE = 50

BIOMAS = {
    1: {"parede": (80,  55,  35), "chao": (45, 32, 20),  "pedra": (120, 90,  60), "minerio": (180, 120, 40),  "agua": (35, 65, 115)},
    2: {"parede": (40,  55,  35), "chao": (25, 35, 20),  "pedra": (70, 100,  55), "minerio": (140,  60, 160), "agua": (25, 80, 95)},
    3: {"parede": (50,  60,  90), "chao": (25, 30, 55),  "pedra": (80,  90, 150), "minerio": ( 80, 220, 220), "agua": (45, 55, 140)},
    4: {"parede": (30,  20,  20), "chao": (20, 12, 12),  "pedra": (60,  40,  35), "minerio": (220,  80,  20),  "agua": (145, 40, 25)}, # Lava
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


class GerenciadorEstados:
    """Controlador central da arquitetura de estados e efeitos de transição."""
    def __init__(self, game):
        self.game = game
        self.estados_registrados = {}
        self.estado_atual = None
        self.transicao = TransicaoFade(velocidade=10)

    def registrar(self, nome, estado_instancia):
        self.estados_registrados[nome] = estado_instancia

    def mudar_estado(self, nome_estado):
        """Dispara uma transição suave por Fade Out -> Fade In."""
        if self.transicao.modo is None:
            self.transicao.iniciar(nome_estado)

    def mudar_estado_imediato(self, nome_estado):
        self.estado_atual = self.estados_registrados[nome_estado]
        if self.estado_atual:
            self.estado_atual.iniciar()

    def handle_event(self, event):
        if self.transicao.modo != 'out' and self.estado_atual:
            self.estado_atual.handle_event(event)

    def atualizar(self):
        self.transicao.atualizar(self)
        if self.transicao.modo != 'out' and self.estado_atual:
            self.estado_atual.atualizar()

    def desenhar(self, tela):
        if self.estado_atual:
            self.estado_atual.desenhar(tela)
        self.transicao.desenhar(tela)


class BlastMiner:
    def __init__(self):
        pygame.init()
        self.tela   = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Blast Miner Co. - State Machine Version")
        self.clock  = pygame.time.Clock()
        self.gerador = GeradorProcedural()

        # Telas originais instanciadas para reaproveitamento nos adaptadores
        self.tela_inicial  = TelaInicial(self.tela)
        self.tela_pause    = TelaPause(self.tela)
        self.tela_gameover = TelaGameOver(self.tela)
        self.tela_loja     = TelaLoja(self.tela)

        # Configuração da FSM (Finite State Machine)
        self.fsm = GerenciadorEstados(self)
        self._configurar_estados()

        # Variáveis globais do mundo
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

    def _configurar_estados(self):
        self.fsm.registrar("menu", EstadoMenuAdaptador(self.fsm))
        self.fsm.registrar("jogo", EstadoJogando(self.fsm))
        self.fsm.registrar("pause", EstadoPauseAdaptador(self.fsm))
        self.fsm.registrar("gameover", EstadoGameOverAdaptador(self.fsm))
        self.fsm.registrar("loja", EstadoLojaAdaptador(self.fsm))
        self.fsm.registrar("dialogo", None) # Modificado dinamicamente ao interagir com NPCs
        
        self.fsm.mudar_estado_imediato("menu")

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
        self.npcs = [
            NPC((sc - 2) * TELA_SIZE, sl * TELA_SIZE, "ferreiro"),
            NPC((sc + 2) * TELA_SIZE, sl * TELA_SIZE, "ambulante"),
        ]

    def _atualizar_camera(self):
        mapa_larg = self.gerador.colunas * TELA_SIZE
        mapa_alt  = self.gerador.linhas  * TELA_SIZE
        self.cam_x = max(0, min(self.player.rect.centerx - LARGURA // 2, mapa_larg - LARGURA))
        self.cam_y = max(0, min(self.player.rect.centery - ALTURA  // 2, mapa_alt  - ALTURA))

    def _processar_frames_jogo(self):
        if self.player.invencivel_timer > 0:
            self.player.invencivel_timer -= 1

        self.player.controlar(self.paredes, self.bombas)

        if not self.player.imune_veneno:
            if hasattr(self.player, '_veneno_timer') and self.player._veneno_timer > 0:
                self.player._veneno_timer -= 1
                if self.player._veneno_timer % 60 == 0:
                    self.player.receber_dano(5)

        for b in self.bombas[:]:
            b.atualizar(self.mapa, self.player, self.inimigos)
            if b.drops_gerados:
                self.itens_chao.extend(b.drops_gerados)
                b.drops_gerados.clear()
            if b.explodiu:
                self.bombas.remove(b)

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

            if not inimigo.ativo:
                drops = gerar_drops_mob(inimigo)
                self.itens_chao.extend(drops)

            if isinstance(inimigo, Golem):
                inimigo.aplicar_knockback_no_player(self.player, self.paredes, self.bombas)
            elif inimigo.rect.colliderect(self.player.rect):
                self.player.receber_dano()

        for s in novos_slimes:
            self.inimigos.append(s)

        for proj in self.projeteis[:]:
            proj.atualizar(self.player, self.paredes)
            if not proj.ativo:
                self.projeteis.remove(proj)

        for item in self.itens_chao[:]:
            tipo_coletado = item.atualizar(self.player)
            if tipo_coletado:
                self.inventario.adicionar(tipo_coletado)
                self.itens_chao.remove(item)

        if not self.saida_aberta and len(self.inimigos) == 0:
            self.saida_aberta = True
            self._spawnar_npcs()

        if self.saida_aberta:
            if self.saida_rect and self.player.rect.colliderect(self.saida_rect):
                self.fase_atual += 1
                self._carregar_fase(primeiro_spawn=False)
                self.fsm.mudar_estado("jogo") # Transição Fade ao entrar na escada!
                return

        if self.player.hp <= 0:
            self.fsm.mudar_estado("gameover")
            return

        self._atualizar_camera()

    def _desenhar_jogo(self):
        self.desenhar_cenario()

        for b in self.bombas:
            rc = pygame.Rect(b.rect.x - self.cam_x, b.rect.y - self.cam_y, b.rect.width, b.rect.height)
            pygame.draw.rect(self.tela, b.cor, rc)

        for item in self.itens_chao: item.desenhar(self.tela, self.cam_x, self.cam_y)
        for proj in self.projeteis: proj.desenhar(self.tela, self.cam_x, self.cam_y)
        for npc in self.npcs: npc.desenhar(self.tela, self.cam_x, self.cam_y)

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

                # Física de colisão adicionada previamente para blocos fora da tela
                if tile in (1, 2, 4, 5):
                    self.paredes.append(rect_mundo)

                if x + TELA_SIZE < 0 or x > LARGURA or y + TELA_SIZE < 0 or y > ALTURA:
                    if tile == 3: self.saida_rect = rect_mundo
                    continue

                if tile == 0:
                    pygame.draw.rect(self.tela, cores["chao"], rect)
                elif tile == 1:
                    pygame.draw.rect(self.tela, cores["parede"], rect)
                    borda = tuple(min(v + 25, 255) for v in cores["parede"])
                    pygame.draw.rect(self.tela, borda, rect, 2)
                elif tile == 2:
                    pygame.draw.rect(self.tela, cores["pedra"], rect)
                    pygame.draw.rect(self.tela, cores["chao"], rect, 2)
                elif tile == 4:
                    pygame.draw.rect(self.tela, cores["minerio"], rect)
                    inner  = pygame.Rect(x + 10, y + 10, TELA_SIZE - 20, TELA_SIZE - 20)
                    brilho = tuple(min(v + 60, 255) for v in cores["minerio"])
                    pygame.draw.rect(self.tela, brilho, inner)
                elif tile == 5:
                    # DESENHO DO NOVO TILE DE ÁGUA (LAGO)
                    pygame.draw.rect(self.tela, cores["agua"], rect)
                    # Detalhes visuais de pequenas ondas reflexivas na água
                    pygame.draw.line(self.tela, (200, 220, 255, 60), (x + 8, y + 20), (x + 22, y + 20), 1)
                    pygame.draw.line(self.tela, (200, 220, 255, 60), (x + 25, y + 35), (x + 40, y + 35), 1)
                elif tile == 3:
                    self.saida_rect = rect_mundo
                    if self.saida_aberta:
                        pygame.draw.rect(self.tela, (20, 20, 20), rect)
                        for degrau in range(3):
                            dy = y + 10 + degrau * 12
                            pygame.draw.rect(self.tela, (200, 160, 80),
                                             pygame.Rect(x + 8 + degrau*5, dy, TELA_SIZE - 16 - degrau*10, 6))
                    else:
                        pygame.draw.rect(self.tela, (80, 20, 20), rect)
                        pygame.draw.rect(self.tela, (180, 40, 40), rect, 3)
                        fonte_c = pygame.font.SysFont("monospace", 22, bold=True)
                        cad = fonte_c.render("🔒", True, (255, 80, 80))
                        self.tela.blit(cad, (x + TELA_SIZE//2 - cad.get_width()//2,
                                             y + TELA_SIZE//2 - cad.get_height()//2))

    def desenhar_hud(self):
        fonte   = pygame.font.SysFont("monospace", 20, bold=True)
        fonte_p = pygame.font.SysFont("monospace", 15)

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

        if self.player.bomba_cooldown > 0:
            tb = fonte.render(f"[RMB] {self.player.bomba_cooldown/60:.1f}s", True, (255, 200, 0))
        else:
            tb = fonte.render("[RMB] BOMBA", True, (100, 255, 100))
        self.tela.blit(tb, (250, ALTURA - 45))

        if self.player.espada_ativa:
            te = fonte.render("[LMB] ESPADA", True, (255, 230, 80))
        elif self.player.espada_cooldown > 0:
            te = fonte.render(f"[LMB] {self.player.espada_cooldown/60:.1f}s", True, (160, 140, 50))
        else:
            te = fonte.render("[LMB] ESPADA", True, (200, 200, 200))
        self.tela.blit(te, (470, ALTURA - 45))

        nomes = {1:"Minas de Terra", 2:"Caverna de Fungos", 3:"Minas de Cristal", 4:"Núcleo Vulcânico"}
        tf = fonte.render(f"FASE {self.fase_atual}  |  {nomes[_bioma(self.fase_atual)]}  [{self.gerador.colunas}x{self.gerador.linhas}]", True, (180, 180, 180))
        self.tela.blit(tf, (LARGURA//2 - tf.get_width()//2, 10))

        if self.saida_aberta:
            msg = fonte.render("✔ SAÍDA ABERTA — aproxime-se de um NPC e aperte [E]", True, (80, 255, 120))
            self.tela.blit(msg, (LARGURA//2 - msg.get_width()//2, 40))

        vivos = len(self.inimigos)
        cor_v = (255, 100, 100) if vivos > 0 else (100, 255, 100)
        tv = fonte_p.render(f"Inimigos: {vivos}", True, cor_v)
        self.tela.blit(tv, (LARGURA - tv.get_width() - 10, 10))

        self._desenhar_barra_status()
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
                cor = (180, 220, 180)
                t = fonte.render(f"{nome[:14]:<14} {qtd}", True, cor)
                self.tela.blit(t, (ix, iy))
                iy += 15

    def _desenhar_prompt_npc(self):
        for npc in self.npcs:
            if npc.perto_do_player(self.player):
                fonte = pygame.font.SysFont("monospace", 16, bold=True)
                rx = npc.rect.x - self.cam_x
                ry = npc.rect.y - self.cam_y - 30
                txt = fonte.render(f"[E] Falar com {npc.nome}", True, (255, 255, 100))
                self.tela.blit(txt, (rx - txt.get_width()//2 + 20, ry))

    def executar(self):
        while self.rodando:
            self.tela.fill((10, 10, 10))
            events = pygame.event.get()
            
            for event in events:
                if event.type == pygame.QUIT:
                    self.rodando = False
                self.fsm.handle_event(event)

            self.fsm.atualizar()
            self.fsm.desenhar(self.tela)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    jogo = BlastMiner()
    jogo.executar()