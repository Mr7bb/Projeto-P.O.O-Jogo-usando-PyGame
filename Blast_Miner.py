import pygame
import random
import sys
import os
 
from config import TELA_SIZE
from Mapas.gerador_mapas import GeradorProcedural
from entidades.Player import Player
from entidades.Fantasma import Fantasma, LegiaoDeFantasmas
from entidades.Golem import Golem
from entidades.GolemLava import GolemLava
from entidades.Cogumelos import CogumeloEsporos, CogumeloAgressivo
from entidades.Goblin import Goblin
from entidades.Slime import Slime
from entidades.NPC import NPC
from entidades.Bosses import Boss, EcoPerdido, Gruk, Mykros, Guardiao, CoracaoDaMina
from objetos.Bomba import Bomba
from objetos.Projetil import Esporo, Lanca, PicaretaFantasma
from objetos.Inventario import Inventario
from objetos.Drops import gerar_drops_mob
from objetos.Item import ITENS
 
from telas.tela_inicial import TelaInicial
from telas.tela_jogo import TelaPause
from telas.tela_gameover import TelaGameOver
from telas.tela_loja import TelaLoja
 
from telas.tela_estado_game import TransicaoFade
from telas.telas_estado_jogo import EstadoJogando
from telas.tela_estado_adaptadores import EstadoMenuAdaptador, EstadoPauseAdaptador, EstadoGameOverAdaptador, EstadoLojaAdaptador
 
_BIOMA1_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sprites', 'Biomas', 'bioma1_sprites')
_BIOMA1_ARQUIVOS = {
    'chao': ['tile_0a.png', 'tile_0b.png'],
    'parede': ['tile_1_costas.png', 'tile_1_dir.png', 'tile_1_esq.png', 'tile_1_fosa.png', 'tile_1_frente.png', 'tile_1_mora.png'],
    'pedra': [f'tile_2_{numero}.png' for numero in range(1, 9)],
    'minerio': [f'tile_2_{numero}.png' for numero in range(1, 9)],
    'saida_fechada': ['tile_3_fechada_1.png', 'tile_3_fechada_2.png'],
    'saida_aberta': ['tile_3_aberta.png'],
    'agua': [f'tile_5_{numero}.png' for numero in range(1, 5)],
}
_BIOMA1_SPRITES = None


def _carregar_sprites_bioma1():
    global _BIOMA1_SPRITES
    if _BIOMA1_SPRITES is not None:
        return _BIOMA1_SPRITES

    def criar_tile(arquivo, tipo):
        imagem = pygame.image.load(os.path.join(_BIOMA1_DIR, arquivo)).convert_alpha()
        tamanho = int(TELA_SIZE * 1.35) if tipo in ('pedra', 'minerio', 'agua') else TELA_SIZE
        imagem = pygame.transform.smoothscale(imagem, (tamanho, tamanho))

        tile = pygame.Surface((TELA_SIZE, TELA_SIZE), pygame.SRCALPHA)
        cor = BIOMAS[1][{'chao': 'chao', 'parede': 'parede', 'pedra': 'pedra', 'minerio': 'minerio', 'saida_fechada': 'chao', 'saida_aberta': 'chao', 'agua': 'agua'}[tipo]]
        pygame.draw.rect(tile, cor, tile.get_rect(), border_radius=4)
        tile.blit(imagem, imagem.get_rect(center=tile.get_rect().center))

        mascara = pygame.Surface((TELA_SIZE, TELA_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=4)
        tile.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tile

    try:
        _BIOMA1_SPRITES = {
            tipo: [criar_tile(arquivo, tipo) for arquivo in arquivos]
            for tipo, arquivos in _BIOMA1_ARQUIVOS.items()
        }
    except pygame.error as erro:
        _BIOMA1_SPRITES = {}
        print(f'[BIOMA 1] nao consegui carregar as sprites: {erro}')
    return _BIOMA1_SPRITES

def _sprite_bioma1(tipo, linha, coluna, animado=False):
    sprites = _carregar_sprites_bioma1().get(tipo, [])
    if not sprites:
        return None
    variacao = linha * 31 + coluna * 17
    if animado:
        variacao += pygame.time.get_ticks() // 220
    return sprites[variacao % len(sprites)]

ALTURA    = 900
LARGURA   = 1200
# TELA_SIZE agora vem do config.py (era definido aqui e copiado em mais uns 3 arquivos)
 
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
 
def _ultima_fase_do_bioma(fase_num):
    # cada bioma tem 3 fases (1-3, 4-6, 7-9, 10-12...), entao a ultima fase de cada
    # bioma sempre e multiplo de 3. usado pra so deixar os npcs aparecerem la.
    return fase_num % 3 == 0
 
def _tabela_spawns(fase_num):
    if fase_num == 1:   return [(Fantasma, 2, 3)]
    elif fase_num == 2: return [(Fantasma, 4, 6)]
    # fase 3 = ultima fase do bioma 1 = sala do boss "O Eco Perdido" (sozinho,
    # igual o Manual de Design de Bosses descreve: nenhum boss deve ser so mais
    # um mob no meio da fase, ele e o combate inteiro)
    elif fase_num == 3: return [(EcoPerdido, 1, 1)]
    # pedido: bem mais slime no bioma dos goblins/slimes (fases 4 a 6)
    elif fase_num == 4: return [(Goblin, 3, 4), (Slime, 6, 8)]
    elif fase_num == 5: return [(Goblin, 4, 5), (Slime, 7, 9), (Fantasma, 2, 3)]
    # fase 6 = ultima fase do bioma 2 = sala do boss "Gruk, o Senhor da Mina Verde"
    elif fase_num == 6: return [(Gruk, 1, 1)]
    elif fase_num == 7: return [(CogumeloEsporos, 2, 3), (CogumeloAgressivo, 2, 3)]
    elif fase_num == 8: return [(CogumeloEsporos, 3, 4), (CogumeloAgressivo, 3, 4), (Goblin, 2, 3), (Slime, 2, 3)]
    # fase 9 = ultima fase do bioma 3 = sala do boss "Mykros, o Coracao da Colonia"
    elif fase_num == 9: return [(Mykros, 1, 1)]
    # pedido: fases finais mais cheias e com mais variedade. golem de lava entra aqui,
    # no mesmo bioma do golem comum
    elif fase_num == 10: return [(Golem, 3, 4), (GolemLava, 1, 2), (Fantasma, 2, 3)]
    elif fase_num == 11: return [(Golem, 4, 5), (GolemLava, 1, 2), (Fantasma, 2, 3), (Slime, 3, 4), (CogumeloEsporos, 1, 2)]
    # fase 12 = ultima fase do bioma 4 = sala do boss "O Guardiao"
    elif fase_num == 12: return [(Guardiao, 1, 1)]
    # fase 13 = bioma 5 (Nucleo Vulcanico) = chefe final "O Coracao da Mina"
    elif fase_num == 13: return [(CoracaoDaMina, 1, 1)]
    else:               return [(Golem, 3, 4), (GolemLava, 2, 3), (Fantasma, 3, 4), (Goblin, 2, 3), (Slime, 2, 3)] 
 
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
        self.tela_cheia = False
 
      
        self._fonte_hud      = pygame.font.SysFont("monospace", 20, bold=True)
        self._fonte_hud_p    = pygame.font.SysFont("monospace", 15)
        self._fonte_status   = pygame.font.SysFont("monospace", 15, bold=True)
        self._fonte_prompt   = pygame.font.SysFont("monospace", 16, bold=True)
        self._fonte_cadeado  = pygame.font.SysFont("monospace", 22, bold=True)
        self._fonte_hotbar_simbolo = pygame.font.SysFont("monospace", 18, bold=True)
        self._fonte_hotbar_qtd     = pygame.font.SysFont("monospace", 12, bold=True)
 
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
            print(f"\n[ERRO CRÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚ÂTICO NA MAQUINA DE ESTADOS]: {e}")
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
 
                # seguranca extra pro bug do fantasma nascendo dentro de bloco solido:
                # o tile escolhido ja devia ser chao livre, mas se o retangulo do mob
                # (que pode ser um pouco maior que o tile) acabar encostando numa parede
                # vizinha, tenta reposicionar num outro candidato da lista antes de desistir.
                if any(mob.rect.colliderect(p) for p in self.paredes):
                    for lin2, col2 in candidatos:
                        x2, y2 = col2 * TELA_SIZE, lin2 * TELA_SIZE
                        mob.rect.x, mob.rect.y = x2, y2
                        if not any(mob.rect.colliderect(p) for p in self.paredes):
                            break
 
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
 
        # Lodo Corrosivo (boss Gruk): se o player estiver em cima de uma poca de lodo,
        # reduz a velocidade dele em 40% nesse frame
        mult_velocidade = 1.0
        for inimigo in self.inimigos:
            if isinstance(inimigo, Gruk):
                for poca in inimigo.pocas_lodo:
                    if poca["rect"].colliderect(self.player.rect):
                        mult_velocidade = 0.6
        self.player.controlar(self.paredes, self.bombas, mult_velocidade)
 
        # veneno (esporo) e fogo (golem de lava) sao os 2 status de dano ao longo do tempo.
        # _veneno_timer/_fogo_timer ja nascem zerados no Player.__init__ agora, entao nao
        # precisa mais checar com hasattr toda hora
        if not self.player.imune_veneno and self.player._veneno_timer > 0:
            self.player._veneno_timer -= 1
            if self.player._veneno_timer % 60 == 0: self.player.receber_dano(5)
 
        if self.player._fogo_timer > 0:
            self.player._fogo_timer -= 1
            if self.player._fogo_timer % 30 == 0: self.player.receber_dano(4)
 
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
                    elif isinstance(inimigo, EcoPerdido): self.projeteis.append(PicaretaFantasma(ox, oy, ax, ay))
                inimigo.projeteis_pendentes.clear()
 
            # invocacoes dos bosses (Invocacao dos Perdidos, Invocar Slimes, Cogumelos
            # Parasitas, etc): cada boss so guarda as posicoes pendentes, quem cria o
            # mob de verdade e o jogo, igual ja acontecia com os projeteis acima
            if hasattr(inimigo, 'invocacoes_pendentes') and inimigo.invocacoes_pendentes:
                for ix, iy in inimigo.invocacoes_pendentes:
                    reforco = None
                    if isinstance(inimigo, EcoPerdido): reforco = Fantasma(ix, iy)
                    elif isinstance(inimigo, Gruk): reforco = Slime(ix, iy, mini=True)
                    elif isinstance(inimigo, Mykros):
                        reforco = CogumeloEsporos(ix, iy)
                        inimigo.parasitas_vivos.append(reforco)
                    elif isinstance(inimigo, CoracaoDaMina): reforco = Goblin(ix, iy)
                    if reforco: novos_slimes.append(reforco)
                inimigo.invocacoes_pendentes.clear()
 
            # bosses: atualiza os golpes em area telegrafados (cada um decide sozinho
            # quando disparar um golpe novo dentro do proprio atualizar_ataques)
            if isinstance(inimigo, Boss): inimigo.atualizar_ataques(self.player, self.paredes, self.mapa)
 
            if hitbox_picareta and not inimigo._atingindo_esse_swing and inimigo.rect.colliderect(hitbox_picareta):
                inimigo._atingindo_esse_swing = True
                dano = self.player.dano_picareta_para(inimigo)
                if isinstance(inimigo, Slime):
                    dividiu = inimigo.receber_dano_picareta(dano, self.player.rect)
                    if dividiu:
                        for _ in range(2):
                            mini = Slime(inimigo.rect.x, inimigo.rect.y, mini=True)
                            # BUG CORRIGIDO: a picareta fica ativa por alguns frames (PICARETA_DURACAO),
                            # entao sem isso os minis nasciam ja "visiveis" pra mesma espadada que
                            # acabou de dividir o slime grande, e no frame seguinte tomavam dano
                            # de novo e morriam na hora ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€šÃ‚Â parecia que 1 hit matava os 3 de uma vez.
                            # marcando como True aqui, eles ficam imunes ATE essa espadada acabar,
                            # e so voltam a poder tomar dano na proxima picaretada de verdade.
                            mini._atingindo_esse_swing = True
                            novos_slimes.append(mini)
                else: inimigo.receber_dano_picareta(dano, self.player.rect)
 
            if not hitbox_picareta: inimigo._atingindo_esse_swing = False
            if not inimigo.ativo: self.itens_chao.extend(gerar_drops_mob(inimigo))
 
            # golem de lava: ataque especial de solo a distancia, roda todo frame
            # (o cooldown/alcance interno dele decide quando realmente bate)
            if isinstance(inimigo, GolemLava): inimigo.atacar_solo(self.player)
 
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
            # pedido: npc so aparece na ultima fase de cada bioma, nao em toda fase
            if _ultima_fase_do_bioma(self.fase_atual):
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
            if isinstance(inimigo, Boss):
                inimigo.desenhar_extra(self.tela, self.cam_x, self.cam_y)
                inimigo.desenhar_ataques(self.tela, self.cam_x, self.cam_y)
 
        self.player.desenhar(self.tela, self.cam_x, self.cam_y)
 
        self.player.desenhar_picareta(self.tela, self.cam_x, self.cam_y)
        self._desenhar_prompt_npc()
        self.desenhar_hud()
 
    def desenhar_cenario(self):
        self.saida_rect = None
        bioma = _bioma(self.fase_atual)
        cores = BIOMAS[bioma]
        usar_sprites = bioma == 1 and bool(_carregar_sprites_bioma1())
        if usar_sprites:
            self.tela.fill(cores['chao'])

        for lin_idx, inline in enumerate(self.mapa):
            for col_idx, tile in enumerate(inline):
                x, y = col_idx * TELA_SIZE - self.cam_x, lin_idx * TELA_SIZE - self.cam_y
                rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)

                if tile == 3:
                    self.saida_rect = pygame.Rect(col_idx * TELA_SIZE, lin_idx * TELA_SIZE, TELA_SIZE, TELA_SIZE)
                if x + TELA_SIZE < 0 or x > LARGURA or y + TELA_SIZE < 0 or y > ALTURA:
                    continue

                if usar_sprites:
                    tipo = {
                        0: 'chao',
                        1: 'parede',
                        2: 'pedra',
                        4: 'minerio',
                        5: 'agua',
                    }.get(tile)
                    if tile == 3:
                        tipo = 'saida_aberta' if self.saida_aberta else 'saida_fechada'
                    sprite = _sprite_bioma1(tipo, lin_idx, col_idx, animado=(tile == 5)) if tipo else None
                    if sprite:
                        self.tela.blit(sprite, rect)
                        continue

                # Visual original, usado nos outros biomas e se algum asset falhar.
                if tile == 0: pygame.draw.rect(self.tela, cores['chao'], rect)
                elif tile == 1:
                    pygame.draw.rect(self.tela, cores['parede'], rect)
                    pygame.draw.rect(self.tela, tuple(min(v + 25, 255) for v in cores['parede']), rect, 2)
                elif tile == 2:
                    pygame.draw.rect(self.tela, cores['pedra'], rect)
                    pygame.draw.rect(self.tela, cores['chao'], rect, 2)
                elif tile == 4:
                    pygame.draw.rect(self.tela, cores['minerio'], rect)
                    pygame.draw.rect(self.tela, tuple(min(v + 60, 255) for v in cores['minerio']), pygame.Rect(x + 10, y + 10, TELA_SIZE - 20, TELA_SIZE - 20))
                elif tile == 5:
                    pygame.draw.rect(self.tela, cores['agua'], rect)
                    pygame.draw.line(self.tela, (255, 255, 255, 40), (x + 8, y + 20), (x + 22, y + 20), 1)
                elif tile == 3:
                    if self.saida_aberta:
                        pygame.draw.rect(self.tela, (20, 20, 20), rect)
                        for d in range(3):
                            pygame.draw.rect(self.tela, (200, 160, 80), pygame.Rect(x + 8 + d * 5, y + 10 + d * 12, TELA_SIZE - 16 - d * 10, 6))
                    else:
                        pygame.draw.rect(self.tela, (80, 20, 20), rect)
                        cad = self._fonte_cadeado.render('LOCKED', True, (255, 80, 80))
                        self.tela.blit(cad, (x + TELA_SIZE // 2 - cad.get_width() // 2, y + TELA_SIZE // 2 - cad.get_height() // 2))
    def desenhar_hud(self):
        # fontes agora vem cacheadas do __init__ (self._fonte_hud / self._fonte_hud_p)
        # em vez de criar novas toda vez que esse metodo roda (que e todo frame)
        fonte, fonte_p = self._fonte_hud, self._fonte_hud_p
        bx, by, bl, ba = 10, ALTURA - 50, 220, 22
        pygame.draw.rect(self.tela, (60, 20, 20), (bx, by, bl, ba), border_radius=4)
        fw = int(bl * self.player.hp_pct)
        if fw > 0: pygame.draw.rect(self.tela, (int(255*(1-self.player.hp_pct)), int(200*self.player.hp_pct), 30), (bx, by, fw, ba), border_radius=4)
        pygame.draw.rect(self.tela, (200, 200, 200), (bx, by, bl, ba), 2, border_radius=4)
        self.tela.blit(fonte_p.render(f"HP  {self.player.hp}/{self.player.hp_max}", True, (255, 255, 255)), (bx + 6, by + 3))
 
        # mostra os 2 status de dano ao longo do tempo (veneno e fogo) empilhados
        # em cima da barra de vida, um de cada vez pra nao sobrepor
        status_y = by - 20
        if not self.player.imune_veneno and self.player._veneno_timer > 0:
            self.tela.blit(fonte_p.render("ENVENENADO", True, (100, 255, 60)), (bx, status_y))
            status_y -= 18
        if self.player._fogo_timer > 0:
            self.tela.blit(fonte_p.render("PEGANDO FOGO", True, (255, 140, 40)), (bx, status_y))
 
        tb = fonte.render(f"[RMB] {self.player.bomba_cooldown/60:.1f}s" if self.player.bomba_cooldown > 0 else "[RMB] BOMBA", True, (255, 200, 0) if self.player.bomba_cooldown > 0 else (100, 255, 100))
        self.tela.blit(tb, (250, ALTURA - 45))
 
        tp = fonte.render(f"[LMB] {self.player.picareta_cooldown/60:.1f}s" if self.player.picareta_cooldown > 0 else "[LMB] PICARETA", True, (160, 140, 50) if self.player.picareta_cooldown > 0 else (200, 200, 200))
        self.tela.blit(tp, (470, ALTURA - 45))
 
        nomes = {1:"Caverna Normal", 2:"Caverna Escura", 3:"Caverna de Fungos", 4:"Caverna de Cristais", 5:"NÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Âºcleo VulcÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢nico"}
        tf = fonte.render(f"FASE {self.fase_atual}  |  {nomes[_bioma(self.fase_atual)]}", True, (180, 180, 180))
        self.tela.blit(tf, (LARGURA//2 - tf.get_width()//2, 10))
 
        if self.saida_aberta: self.tela.blit(fonte.render("SAÍDA ABERTA — aproxime-se de um NPC e aperte [E]", True, (80, 255, 120)), (LARGURA//2 - 250, 40))
        self.tela.blit(fonte_p.render(f"Inimigos: {len(self.inimigos)}", True, (255, 100, 100) if len(self.inimigos) > 0 else (100, 255, 100)), (LARGURA - 130, 10))
        self._desenhar_barra_status()
        self._desenhar_barra_boss()
        
        self._desenhar_inventario_hud()
 
    def _desenhar_barra_status(self):
        fonte, p = self._fonte_status, self.player
        items = [
            ('FORCA', p.nivel_forca, 5),
            ('VEL', p.nivel_velocidade, 4),
            ('VIDA', p.nivel_hp, 5),
            ('BOMBA', p.nivel_bomba_alcance, 3),
            ('PAVIO', p.nivel_bomba_cd, 3),
        ]
        sx, sy = 10, 60
        for label, nivel, maximo in items:
            barra = '#' * nivel + '-' * (maximo - nivel)
            self.tela.blit(fonte.render(f'{label}: [{barra}]', True, (200, 200, 255)), (sx, sy))
            sy += 22
    def _desenhar_barra_boss(self):
        # procura um boss vivo entre os inimigos da fase e desenha a barra de vida
        # grande e centralizada no topo, no estilo classico de luta contra chefe
        boss = next((i for i in self.inimigos if isinstance(i, Boss) and i.ativo), None)
        if not boss: return
 
        bl, ba = 480, 26
        bx, by = LARGURA // 2 - bl // 2, 60
        pct = max(0.0, boss.vida / boss.vida_max)
 
        nome = self._fonte_hud.render(boss.NOME_EXIBICAO, True, (255, 220, 220))
        self.tela.blit(nome, (LARGURA // 2 - nome.get_width() // 2, by - 24))
 
        pygame.draw.rect(self.tela, (40, 10, 10), (bx, by, bl, ba), border_radius=4)
        fw = int(bl * pct)
        if fw > 0: pygame.draw.rect(self.tela, (200, 40, 40), (bx, by, fw, ba), border_radius=4)
        pygame.draw.rect(self.tela, (255, 255, 255), (bx, by, bl, ba), 2, border_radius=4)
 
    def _desenhar_inventario_hud(self):
        itens_ativos = [(nome, qtd) for nome, qtd in self.inventario.itens.items() if qtd > 0]
        if not itens_ativos:
            return
 
        tam_slot, espaco = 52, 4
        largura_total = len(itens_ativos) * (tam_slot + espaco) - espaco
        x_inicial = LARGURA // 2 - largura_total // 2
        y = ALTURA - 130   
 
        for i, (nome, qtd) in enumerate(itens_ativos):
            sx = x_inicial + i * (tam_slot + espaco)
            slot_rect = pygame.Rect(sx, y, tam_slot, tam_slot)
 
            pygame.draw.rect(self.tela, (20, 20, 35), slot_rect, border_radius=6)
            pygame.draw.rect(self.tela, (90, 90, 140), slot_rect, 2, border_radius=6)

            info = ITENS.get(nome, {"cor": (200, 200, 200), "simbolo": "?"})
            pygame.draw.circle(self.tela, info["cor"], slot_rect.center, tam_slot // 2 - 8)
 
            simbolo_txt = self._fonte_hotbar_simbolo.render(info["simbolo"], True, (20, 20, 20))
            self.tela.blit(simbolo_txt, simbolo_txt.get_rect(center=slot_rect.center))
 
            qtd_txt = self._fonte_hotbar_qtd.render(str(qtd), True, (255, 255, 255))
            self.tela.blit(qtd_txt, (slot_rect.right - qtd_txt.get_width() - 3, slot_rect.bottom - qtd_txt.get_height() - 1))
 
    def _desenhar_prompt_npc(self):
        for npc in self.npcs:
            if npc.perto_do_player(self.player):
                txt = self._fonte_prompt.render(f"[E] Falar com {npc.nome}", True, (255, 255, 100))
                self.tela.blit(txt, (npc.rect.x - self.cam_x - txt.get_width()//2 + 20, npc.rect.y - self.cam_y - 30))
 
    def _alternar_tela_cheia(self):
        self.tela_cheia = not self.tela_cheia
        try:
            if self.tela_cheia:
                self.tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN | pygame.SCALED)
            else:
                self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        except pygame.error:
            try:
                flags = pygame.FULLSCREEN if self.tela_cheia else 0
                self.tela = pygame.display.set_mode((LARGURA, ALTURA), flags)
            except pygame.error:
                print("[TELA CHEIA] Esse PC nao suportou nenhum modo de tela cheia, voltando pra janela normal.")
                self.tela_cheia = False
                self.tela = pygame.display.set_mode((LARGURA, ALTURA))
 
        # cada uma dessas telas guardou a superficie antiga como atributo proprio no
        # __init__, entao precisa atualizar a referencia manualmente pra nao ficarem
        # desenhando numa superficie que nao existe mais
        self.tela_inicial.tela  = self.tela
        self.tela_pause.tela    = self.tela
        self.tela_gameover.tela = self.tela
        self.tela_loja.tela     = self.tela
 
    def executar(self):
        while self.rodando:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: self.rodando = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self._alternar_tela_cheia()
                self.fsm.handle_event(event)
            self.fsm.atualizar()
            self.fsm.desenhar(self.tela)
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
 
if __name__ == "__main__":
    jogo = BlastMiner()
    jogo.executar()