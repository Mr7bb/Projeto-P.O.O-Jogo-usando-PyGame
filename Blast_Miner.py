import pygame
import random
import sys

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

from telas.tela_estado_game import TransicaoFade
from telas.telas_estado_jogo import EstadoJogando
from telas.tela_estado_adaptadores import EstadoMenuAdaptador, EstadoPauseAdaptador, EstadoGameOverAdaptador, EstadoLojaAdaptador

ALTURA    = 900
LARGURA   = 1200
TELA_SIZE = 50

BIOMAS = {
    1: {"parede": (60, 70, 80),   "chao": (90, 102, 114), "pedra": (140, 150, 160), "minerio": (120, 130, 140), "agua": (45, 65, 115)},  
    2: {"parede": (42, 46, 31),   "chao": (46, 42, 30),   "pedra": (74, 82, 60),    "minerio": (100, 110, 90),  "agua": (30, 75, 90)},   
    3: {"parede": (31, 46, 26),   "chao": (51, 66, 42),   "pedra": (80, 50, 95),    "minerio": (160, 100, 230), "agua": (45, 50, 120)},  
    4: {"parede": (26, 35, 51),   "chao": (40, 55, 75),   "pedra": (95, 225, 255),  "minerio": (50, 190, 230),  "agua": (50, 120, 180)}, 
    5: {"parede": (43, 14, 14),   "chao": (25, 20, 20),   "pedra": (90, 30, 30),    "minerio": (255, 180, 40),  "agua": (230, 70, 20)},  
}

def _bioma(fase_num):
    if fase_num <= 3: return 1
    if fase_num <= 6: return 2
    if fase_num <= 9: return 3
    if fase_num <= 12: return 4
    return 5

def _tabela_spawns(fase_num):
    if fase_num == 1:   return [(Fantasma, 2, 3)]
    elif fase_num == 2: return [(Fantasma, 4, 6)]
    elif fase_num == 3: return [(Fantasma, 3, 4), (LegiaoDeFantasmas, 3, 4)]
    elif fase_num == 4: return [(Goblin, 3, 4), (Slime, 3, 4)]
    elif fase_num == 5: return [(Goblin, 4, 5), (Slime, 4, 5), (Fantasma, 2, 3)]
    elif fase_num == 6: return [(Goblin, 5, 6), (Slime, 5, 6), (Fantasma, 3, 4), (LegiaoDeFantasmas, 1, 2)]
    elif fase_num == 7: return [(CogumeloEsporos, 2, 3), (CogumeloAgressivo, 2, 3)]
    elif fase_num == 8: return [(CogumeloEsporos, 3, 4), (CogumeloAgressivo, 3, 4), (Goblin, 2, 3), (Slime, 2, 3)]
    elif fase_num == 9: return [(CogumeloEsporos, 3, 4), (CogumeloAgressivo, 2, 3), (Goblin, 2, 3), (Slime, 2, 3), (Fantasma, 2, 3)]
    elif fase_num == 10: return [(Golem, 3, 4)]
    elif fase_num == 11: return [(Golem, 4, 5), (Fantasma, 2, 3), (Slime, 2, 3), (CogumeloEsporos, 1, 2)]
    elif fase_num == 12: return [(Golem, 3, 4), (Fantasma, 2, 3), (Goblin, 2, 3), (Slime, 2, 3), (CogumeloEsporos, 2, 2), (CogumeloAgressivo, 2, 2)]
    else:               return [(Golem, 2, 3), (Fantasma, 2, 2)] 

class GerenciadorEstados:
    def __init__(self, game):
        self.game = game
        self.estados_registrados = {}
        self.estado_atual = None
        self.transicao = TransicaoFade(velocidade=12)

    def registrar(self, nome, estado_instancia): self.estados_registrados[nome] = estado_instancia
    def mudar_estado(self, nome_estado):
        if self.transicao.modo is None: self.transicao.iniciar(nome_estado)
    def mudar_estado_imediato(self, nome_estado):
        self.estado_atual = self.estados_registrados[nome_estado]
        if self.estado_atual: self.estado_atual.iniciar()
    def handle_event(self, event):
        if self.transicao.modo != 'out' and self.estado_atual: self.estado_atual.handle_event(event)
    def atualizar(self):
        self.transicao.atualizar(self)
        if self.transicao.modo != 'out' and self.estado_atual: self.estado_atual.atualizar()
    def desenhar(self, tela):
        if self.estado_atual: self.estado_atual.desenhar(tela)
        self.transicao.desenhar(tela)

class BlastMiner:
    def __init__(self):
        pygame.init()
        self.tela   = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Blast Miner Co.")
        self.clock  = pygame.time.Clock()
        self.gerador = GeradorProcedural()

        self.tela_inicial  = TelaInicial(self.tela)
        self.tela_pause    = TelaPause(self.tela)
        self.tela_gameover = TelaGameOver(self.tela)
        self.tela_loja     = TelaLoja(self.tela)

        self.fsm = GerenciadorEstados(self)
        self._configurar_estados()

        self.player, self.inventario, self.mapa = None, None, None
        self.inimigos = self.paredes = self.bombas = self.projeteis = self.itens_chao = self.npcs = []
        self.saida_rect = None
        self.saida_aberta = False
        self.rodando = True
        self.cam_x = self.cam_y = 0

    def _configurar_estados(self):
        try:
            self.fsm.registrar("menu", EstadoMenuAdaptador(self.fsm))
            self.fsm.registrar("jogo", EstadoJogando(self.fsm))
            self.fsm.registrar("pause", EstadoPauseAdaptador(self.fsm))
            self.fsm.registrar("gameover", EstadoGameOverAdaptador(self.fsm))
            self.fsm.registrar("loja", EstadoLojaAdaptador(self.fsm))
            self.fsm.registrar("dialogo", None)
            self.fsm.mudar_estado_imediato("menu")
        except Exception as e:
            print(f"\n[ERRO CRÍTICO NA MAQUINA DE ESTADOS]: {e}")
            import traceback
            traceback.print_exc()
            pygame.quit()
            sys.exit()

    def _resetar_jogo(self):
        self.player, self.inventario, self.fase_atual, self.rodando = Player(), Inventario(), 1, True
        self._carregar_fase(primeiro_spawn=True)

    def _carregar_fase(self, primeiro_spawn=False):
        self.bombas, self.projeteis, self.itens_chao, self.npcs, self.saida_rect, self.saida_aberta = [], [], [], [], None, False
        self.mapa = self.gerador.gerar_fase(self.fase_atual)

        if primeiro_spawn:
            self.player.rect.topleft = (TELA_SIZE + 5, TELA_SIZE + 5)
        else:
            livres = self.gerador.listar_chao_livre_acessivel(self.mapa)
            lin, col = random.choice(livres) if livres else (1, 1)
            self.player.rect.topleft = (col * TELA_SIZE + 5, lin * TELA_SIZE + 5)

        self._cache_paredes_fisicas()
        self._spawnar_inimigos()

    def _cache_paredes_fisicas(self):
        self.paredes = []
        for lin_idx, linha in enumerate(self.mapa):
            for col_idx, tile in enumerate(linha):
                if tile in (1, 2, 4, 5): 
                    self.paredes.append(pygame.Rect(col_idx * TELA_SIZE, lin_idx * TELA_SIZE, TELA_SIZE, TELA_SIZE))

    def _spawnar_inimigos(self):
        self.inimigos = []
        origem_lin, origem_col = self.player.rect.centery // TELA_SIZE, self.player.rect.centerx // TELA_SIZE
        candidatos = self.gerador.listar_chao_livre_acessivel(self.mapa, excluir_raio=5, origem=(origem_lin, origem_col))

        legiao_atual = []
        for classe, qtd_min, qtd_max in _tabela_spawns(self.fase_atual):
            qtd = random.randint(qtd_min, qtd_max)
            posicoes = random.sample(candidatos, min(qtd, len(candidatos)))
            for lin, col in posicoes:
                x, y = col * TELA_SIZE, lin * TELA_SIZE
                if classe is LegiaoDeFantasmas:
                    mob = LegiaoDeFantasmas(x, y, grupo=legiao_atual)
                    legiao_atual.append(mob)
                else: mob = classe(x, y)
                self.inimigos.append(mob)

    def _spawnar_npcs(self):
        if not self.saida_rect: 
            return

        sc, sl = self.saida_rect.x // TELA_SIZE, self.saida_rect.y // TELA_SIZE
        vagas = self.gerador.achar_vagas_vendedores_bfs(self.mapa, sl, sc)
        if len(vagas) >= 2:
            self.npcs = [NPC(vagas[0][1] * TELA_SIZE, vagas[0][0] * TELA_SIZE, "ferreiro"), NPC(vagas[1][1] * TELA_SIZE, vagas[1][0] * TELA_SIZE, "ambulante")]
        elif len(vagas) == 1:
            self.npcs = [NPC(vagas[0][1] * TELA_SIZE, vagas[0][0] * TELA_SIZE, "ferreiro")]
        else:
            self.npcs = []

    def _atualizar_camera(self):
        mapa_larg, mapa_alt = self.gerador.colunas * TELA_SIZE, self.gerador.linhas * TELA_SIZE
        self.cam_x = max(0, min(self.player.rect.centerx - LARGURA // 2, mapa_larg - LARGURA))
        self.cam_y = max(0, min(self.player.rect.centery - ALTURA  // 2, mapa_alt  - ALTURA))

    def _processar_frames_jogo(self):
        if self.player.invencivel_timer > 0: self.player.invencivel_timer -= 1
        self.player.controlar(self.paredes, self.bombas)

        if not self.player.imune_veneno and hasattr(self.player, '_veneno_timer') and self.player._veneno_timer > 0:
            self.player._veneno_timer -= 1
            if self.player._veneno_timer % 60 == 0: self.player.receber_dano(5)

        for b in self.bombas[:]:
            b.atualizar(self.mapa, self.player, self.inimigos)
            if b.drops_gerados:
                self.itens_chao.extend(b.drops_gerados)
                b.drops_gerados.clear()
            if b.explodiu:
                self.bombas.remove(b)
                self._cache_paredes_fisicas()

        self.inimigos = [i for i in self.inimigos if i.ativo]
        novos_slimes, hitbox_picareta = [], self.player.hitbox_picareta_atual()

        for inimigo in self.inimigos:
            inimigo.mover(self.player, self.paredes, self.mapa, self.bombas)

            if hasattr(inimigo, 'projeteis_pendentes') and inimigo.projeteis_pendentes:
                for ox, oy, ax, ay in inimigo.projeteis_pendentes:
                    if isinstance(inimigo, CogumeloEsporos): self.projeteis.append(Esporo(ox, oy, ax, ay))
                    elif isinstance(inimigo, Goblin): self.projeteis.append(Lanca(ox, oy, ax, ay))
                inimigo.projeteis_pendentes.clear()

            if hitbox_picareta and not inimigo._atingindo_esse_swing and inimigo.rect.colliderect(hitbox_picareta):
                inimigo._atingindo_esse_swing = True
                dano = self.player.dano_picareta_para(inimigo)
                if isinstance(inimigo, Slime):
                    dividiu = inimigo.receber_dano_picareta(dano, self.player.rect)
                    if dividiu:
                        for _ in range(2): novos_slimes.append(Slime(inimigo.rect.x, inimigo.rect.y, mini=True))
                else: inimigo.receber_dano_picareta(dano, self.player.rect)

            if not hitbox_picareta: inimigo._atingindo_esse_swing = False
            if not inimigo.ativo: self.itens_chao.extend(gerar_drops_mob(inimigo))

            if isinstance(inimigo, Golem): inimigo.aplicar_knockback_no_player(self.player, self.paredes, self.bombas)
            elif inimigo.rect.colliderect(self.player.rect): self.player.receber_dano()

        for s in novos_slimes: self.inimigos.append(s)
        for proj in self.projeteis[:]:
            proj.atualizar(self.player, self.paredes)
            if not proj.ativo: self.projeteis.remove(proj)

        for item in self.itens_chao[:]:
            tipo_coletado = item.atualizar(self.player)
            if tipo_coletado:
                self.inventario.adicionar(tipo_coletado)
                self.itens_chao.remove(item)

        if not self.saida_aberta and len(self.inimigos) == 0:
            self.saida_aberta = True
            self._spawnar_npcs()

        if self.saida_aberta and self.saida_rect and self.player.rect.colliderect(self.saida_rect):
            self.fase_atual += 1
            self._carregar_fase(primeiro_spawn=False)
            self.fsm.mudar_estado("jogo")
            return

        if self.player.hp <= 0: self.fsm.mudar_estado("gameover")
        self._atualizar_camera()

    def _desenhar_jogo(self):
        self.desenhar_cenario()
        for b in self.bombas:
            pygame.draw.rect(self.tela, b.cor, pygame.Rect(b.rect.x - self.cam_x, b.rect.y - self.cam_y, TELA_SIZE, TELA_SIZE))
        for item in self.itens_chao: item.desenhar(self.tela, self.cam_x, self.cam_y)
        for proj in self.projeteis: proj.desenhar(self.tela, self.cam_x, self.cam_y)
        for npc in self.npcs: npc.desenhar(self.tela, self.cam_x, self.cam_y)

        for inimigo in self.inimigos:
            ro = inimigo.rect.copy()
            inimigo.rect = pygame.Rect(inimigo.rect.x - self.cam_x, inimigo.rect.y - self.cam_y, inimigo.rect.width, inimigo.rect.height)
            inimigo.desenhar(self.tela)
            inimigo.rect = ro

        pr = pygame.Rect(self.player.rect.x - self.cam_x, self.player.rect.y - self.cam_y, self.player.rect.width, self.player.rect.height)
        if self.player.invencivel_timer % 4 < 2: pygame.draw.rect(self.tela, (255, 200, 0), pr)

        self.player.desenhar_picareta(self.tela, self.cam_x, self.cam_y)
        self._desenhar_prompt_npc()
        self.desenhar_hud()

    def desenhar_cenario(self):
        self.saida_rect = None
        cores = BIOMAS[_bioma(self.fase_atual)]

        for lin_idx, inline in enumerate(self.mapa):
            for col_idx, tile in enumerate(inline):
                x, y = col_idx * TELA_SIZE - self.cam_x, lin_idx * TELA_SIZE - self.cam_y
                rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)

                if tile == 3: self.saida_rect = pygame.Rect(col_idx * TELA_SIZE, lin_idx * TELA_SIZE, TELA_SIZE, TELA_SIZE)
                if x + TELA_SIZE < 0 or x > LARGURA or y + TELA_SIZE < 0 or y > ALTURA: continue

                if tile == 0: pygame.draw.rect(self.tela, cores["chao"], rect)
                elif tile == 1:
                    pygame.draw.rect(self.tela, cores["parede"], rect)
                    pygame.draw.rect(self.tela, tuple(min(v+25, 255) for v in cores["parede"]), rect, 2)
                elif tile == 2:
                    pygame.draw.rect(self.tela, cores["pedra"], rect)
                    pygame.draw.rect(self.tela, cores["chao"], rect, 2)
                elif tile == 4:
                    pygame.draw.rect(self.tela, cores["minerio"], rect)
                    pygame.draw.rect(self.tela, tuple(min(v+60, 255) for v in cores["minerio"]), pygame.Rect(x+10, y+10, TELA_SIZE-20, TELA_SIZE-20))
                elif tile == 5:
                    pygame.draw.rect(self.tela, cores["agua"], rect)
                    pygame.draw.line(self.tela, (255, 255, 255, 40), (x+8, y+20), (x+22, y+20), 1)
                elif tile == 3:
                    if self.saida_aberta:
                        pygame.draw.rect(self.tela, (20, 20, 20), rect)
                        for d in range(3): pygame.draw.rect(self.tela, (200, 160, 80), pygame.Rect(x+8+d*5, y+10+d*12, TELA_SIZE-16-d*10, 6))
                    else:
                        pygame.draw.rect(self.tela, (80, 20, 20), rect)
                        cad = pygame.font.SysFont("monospace", 22, bold=True).render("🔒", True, (255, 80, 80))
                        self.tela.blit(cad, (x + TELA_SIZE//2 - cad.get_width()//2, y + TELA_SIZE//2 - cad.get_height()//2))

    def desenhar_hud(self):
        fonte, fonte_p = pygame.font.SysFont("monospace", 20, bold=True), pygame.font.SysFont("monospace", 15)
        bx, by, bl, ba = 10, ALTURA - 50, 220, 22
        pygame.draw.rect(self.tela, (60, 20, 20), (bx, by, bl, ba), border_radius=4)
        fw = int(bl * self.player.hp_pct)
        if fw > 0: pygame.draw.rect(self.tela, (int(255*(1-self.player.hp_pct)), int(200*self.player.hp_pct), 30), (bx, by, fw, ba), border_radius=4)
        pygame.draw.rect(self.tela, (200, 200, 200), (bx, by, bl, ba), 2, border_radius=4)
        self.tela.blit(fonte_p.render(f"HP  {self.player.hp}/{self.player.hp_max}", True, (255, 255, 255)), (bx + 6, by + 3))

        if not self.player.imune_veneno and hasattr(self.player, '_veneno_timer') and self.player._veneno_timer > 0:
            self.tela.blit(fonte_p.render("☠ ENVENENADO", True, (100, 255, 60)), (bx, by - 20))

        tb = fonte.render(f"[RMB] {self.player.bomba_cooldown/60:.1f}s" if self.player.bomba_cooldown > 0 else "[RMB] BOMBA", True, (255, 200, 0) if self.player.bomba_cooldown > 0 else (100, 255, 100))
        self.tela.blit(tb, (250, ALTURA - 45))

        tp = fonte.render(f"[LMB] {self.player.picareta_cooldown/60:.1f}s" if self.player.picareta_cooldown > 0 else "[LMB] PICARETA", True, (160, 140, 50) if self.player.picareta_cooldown > 0 else (200, 200, 200))
        self.tela.blit(tp, (470, ALTURA - 45))

        nomes = {1:"Caverna Normal", 2:"Caverna Escura", 3:"Caverna de Fungos", 4:"Caverna de Cristais", 5:"Núcleo Vulcânico"}
        tf = fonte.render(f"FASE {self.fase_atual}  |  {nomes[_bioma(self.fase_atual)]}", True, (180, 180, 180))
        self.tela.blit(tf, (LARGURA//2 - tf.get_width()//2, 10))

        if self.saida_aberta: self.tela.blit(fonte.render("✔ SAÍDA ABERTA — aproxime-se de um NPC e aprete [E]", True, (80, 255, 120)), (LARGURA//2 - 250, 40))
        self.tela.blit(fonte_p.render(f"Inimigos: {len(self.inimigos)}", True, (255, 100, 100) if len(self.inimigos) > 0 else (100, 255, 100)), (LARGURA - 130, 10))
        self._desenhar_barra_status()
        
        # ALTERAÇÃO: Inventário agora desenha de forma fixa e permanente na tela
        self._desenhar_inventario_hud()

    def _desenhar_barra_status(self):
        fonte, p = pygame.font.SysFont("monospace", 15, bold=True), self.player
        items = [("⚔", "Força", p.nivel_forca, 5), ("💨", "Vel", p.nivel_velocidade, 4), ("❤", "Vida", p.nivel_hp, 5), ("💣", "Bomba", p.nivel_bomba_alcance, 3), ("⏱", "Pavio", p.nivel_bomba_cd, 3)]
        sx, sy = 10, 60
        for icone, label, nivel, maximo in items:
            self.tela.blit(fonte.render(f"{icone} {label}: {'■'*nivel}{'□'*(maximo-nivel)}", True, (200, 200, 255)), (sx, sy))
            sy += 22

    def _desenhar_inventario_hud(self):
        """ALTERAÇÃO: Desenha uma caixa fixa no canto superior direito para monitoramento claro dos minérios obtidos."""
        ix, iy = LARGURA - 190, 35
        pygame.draw.rect(self.tela, (15, 15, 30, 195), (ix - 5, iy - 5, 185, 190), border_radius=6)
        pygame.draw.rect(self.tela, (70, 70, 120), (ix - 5, iy - 5, 185, 190), 1, border_radius=6)

        titulo = pygame.font.SysFont("monospace", 13, bold=True).render("🎒 INVENTÁRIO", True, (180, 180, 255))
        self.tela.blit(titulo, (ix, iy))
        iy += 20

        fonte = pygame.font.SysFont("monospace", 12)
        contador = 0
        for nome, qtd in self.inventario.itens.items():
            if qtd > 0:
                t = fonte.render(f"{nome[:14]:<14} x{qtd}", True, (180, 220, 180))
                self.tela.blit(t, (ix, iy))
                iy += 16
                contador += 1
                
        if contador == 0:
            self.tela.blit(fonte.render("(Vazio)", True, (120, 120, 140)), (ix, iy))

    def _desenhar_prompt_npc(self):
        for npc in self.npcs:
            if npc.perto_do_player(self.player):
                txt = pygame.font.SysFont("monospace", 16, bold=True).render(f"[E] Falar com {npc.nome}", True, (255, 255, 100))
                self.tela.blit(txt, (npc.rect.x - self.cam_x - txt.get_width()//2 + 20, npc.rect.y - self.cam_y - 30))

    def executar(self):
        while self.rodando:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: self.rodando = False
                self.fsm.handle_event(event)
            self.fsm.atualizar()
            self.fsm.desenhar(self.tela)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    jogo = BlastMiner()
    jogo.executar()