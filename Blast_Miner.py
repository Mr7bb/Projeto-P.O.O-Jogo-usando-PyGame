import pygame
import random
import sys
import os
 
from config import TELA_SIZE, FASE_INICIAL, FASE_FINAL
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
from sons import iniciar_sons, tocar
 
from telas.tela_inicial import TelaInicial
from telas.tela_jogo import TelaPause
from telas.tela_gameover import TelaGameOver
from telas.tela_loja import TelaLoja
from telas.tela_vitoria import TelaVitoria
 
from telas.tela_estado_game import TransicaoFade
from telas.telas_estado_jogo import EstadoJogando
from telas.tela_estado_adaptadores import EstadoMenuAdaptador, EstadoPauseAdaptador, EstadoGameOverAdaptador, EstadoLojaAdaptador, EstadoVitoriaAdaptador
 
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

_BIOMA2_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sprites', 'Biomas', 'bioma2_sprites')
_BIOMA2_ARQUIVOS = {
    'chao': ['tile_0a.png', 'tile_0a.png'],
    'parede': ['tile_1_mud_back.png', 'tile_1_mud_front.png', 'tile_1_mud_left.png', 'tile_1_mud_right.png'],
    'pedra': [f'tile_2_{numero}.png' for numero in range(1, 5)],
    'minerio': ['tile_4_minerio.png'],
    'saida_fechada': ['tile_3_fechada.png'],
    'saida_aberta': ['tile_3_aberta.png'],
    'agua': ['tile_1_mud_back.png'],
}
_BIOMA2_SPRITES = None

_BIOMA3_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sprites', 'Biomas', 'bioma3_sprites')
_BIOMA3_ARQUIVOS = {
    'chao': ['tile_0a.png'],
    'parede': ['tile_1_back_1.png', 'tile_1_back_2.png', 'tile_1_front_1.png', 'tile_1_front_2.png'],
    'pedra': [f'tile_2_{numero}.png' for numero in range(1, 5)],
    'minerio': [f'tile_4_{numero}.png' for numero in range(1, 5)],
    'saida_fechada': ['tile_3_fechada_1.png', 'tile_3_fechada_2.png'],
    'saida_aberta': ['tile_3_aberta.png'],
    # A agua usa as paredes, como solicitado, para continuar bloqueando o caminho.
    'agua': ['tile_1_back_1.png'],
}
_BIOMA3_SPRITES = None


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
        pygame.draw.rect(tile, cor, tile.get_rect(), border_radius=6)
        tile.blit(imagem, imagem.get_rect(center=tile.get_rect().center))

        mascara = pygame.Surface((TELA_SIZE, TELA_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=6)
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


def _carregar_sprites_bioma2():
    global _BIOMA2_SPRITES
    if _BIOMA2_SPRITES is not None:
        return _BIOMA2_SPRITES

    def criar_tile(arquivo, tipo):
        imagem = pygame.image.load(os.path.join(_BIOMA2_DIR, arquivo)).convert_alpha()
        tamanho = int(TELA_SIZE * 1.35) if tipo in ('pedra', 'minerio') else TELA_SIZE
        imagem = pygame.transform.smoothscale(imagem, (tamanho, tamanho))

        tile = pygame.Surface((TELA_SIZE, TELA_SIZE), pygame.SRCALPHA)
        cor = BIOMAS[2][{'chao': 'chao', 'parede': 'parede', 'pedra': 'pedra', 'minerio': 'minerio', 'saida_fechada': 'chao', 'saida_aberta': 'chao', 'agua': 'parede'}[tipo]]
        pygame.draw.rect(tile, cor, tile.get_rect(), border_radius=6)
        tile.blit(imagem, imagem.get_rect(center=tile.get_rect().center))

        # Recorta a imagem que ocupa todo o tile para os cantos da parede
        # acompanharem o arredondamento do fundo.
        if tipo in ('parede', 'agua'):
            mascara = pygame.Surface((TELA_SIZE, TELA_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=6)
            tile.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tile

    try:
        _BIOMA2_SPRITES = {
            tipo: [criar_tile(arquivo, tipo) for arquivo in arquivos]
            for tipo, arquivos in _BIOMA2_ARQUIVOS.items()
        }
    except pygame.error as erro:
        _BIOMA2_SPRITES = {}
        print(f'[BIOMA 2] nao consegui carregar as sprites: {erro}')
    return _BIOMA2_SPRITES


def _sprite_bioma2(tipo, linha, coluna, animado=False):
    sprites = _carregar_sprites_bioma2().get(tipo, [])
    if not sprites:
        return None
    variacao = linha * 31 + coluna * 17
    if animado:
        variacao += pygame.time.get_ticks() // 220
    return sprites[variacao % len(sprites)]


def _carregar_sprites_bioma3():
    global _BIOMA3_SPRITES
    if _BIOMA3_SPRITES is not None:
        return _BIOMA3_SPRITES

    def criar_tile(arquivo, tipo):
        diretorio = _BIOMA2_DIR if tipo == 'chao' else _BIOMA3_DIR
        nome_arquivo = 'tile_0a.png' if tipo == 'chao' else arquivo
        imagem = pygame.image.load(os.path.join(diretorio, nome_arquivo)).convert_alpha()
        tamanho = int(TELA_SIZE * 1.35) if tipo in ('pedra', 'minerio') else TELA_SIZE
        imagem = pygame.transform.smoothscale(imagem, (tamanho, tamanho))

        tile = pygame.Surface((TELA_SIZE, TELA_SIZE), pygame.SRCALPHA)
        cor = BIOMAS[3][{'chao': 'chao', 'parede': 'parede', 'pedra': 'pedra', 'minerio': 'minerio', 'saida_fechada': 'chao', 'saida_aberta': 'chao', 'agua': 'parede'}[tipo]]
        pygame.draw.rect(tile, cor, tile.get_rect(), border_radius=6)

        tile.blit(imagem, imagem.get_rect(center=tile.get_rect().center))

        if tipo in ('parede', 'agua'):
            mascara = pygame.Surface((TELA_SIZE, TELA_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=6)
            tile.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return tile

    try:
        _BIOMA3_SPRITES = {
            tipo: [criar_tile(arquivo, tipo) for arquivo in arquivos]
            for tipo, arquivos in _BIOMA3_ARQUIVOS.items()
        }
    except pygame.error as erro:
        _BIOMA3_SPRITES = {}
        print(f'[BIOMA 3] nao consegui carregar as sprites: {erro}')
    return _BIOMA3_SPRITES


def _sprite_bioma3(tipo, linha, coluna, animado=False):
    # Uma mistura deterministica elimina as faixas diagonais que surgiam ao
    # usar apenas uma soma linear de linha e coluna.
    variacao = (linha * 374761393 + coluna * 668265263) & 0xFFFFFFFF
    variacao = (variacao ^ (variacao >> 13)) * 1274126177 & 0xFFFFFFFF

    sprites = _carregar_sprites_bioma3().get(tipo, [])
    if not sprites:
        return None
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
    elif fase_num == 2: return [(LegiaoDeFantasmas, 4, 6)]
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
    elif fase_num == FASE_FINAL: return [(CoracaoDaMina, 1, 1)]
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
        iniciar_sons()
        self.tela   = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Blast Miner Co.")
        self.clock  = pygame.time.Clock()
        self.gerador = GeradorProcedural()
 
        self.tela_inicial  = TelaInicial(self.tela)
        self.tela_pause    = TelaPause(self.tela)
        self.tela_gameover = TelaGameOver(self.tela)
        self.tela_loja     = TelaLoja(self.tela)
        self.tela_vitoria  = TelaVitoria(self.tela)
 
        self.fsm = GerenciadorEstados(self)
        self._configurar_estados()
 
        self.player, self.inventario, self.mapa = None, None, None
        self.inimigos = []
        self.paredes = []
        self.paredes_projeteis = []
        self.bombas = []
        self.projeteis = []
        self.itens_chao = []
        self.npcs = []
        self.saida_rect = None
        self.saida_aberta = False
        self.rodando = True
        self.cam_x = self.cam_y = 0
        self.tela_cheia = False
 
      
        self._fonte_hud      = pygame.font.SysFont("trebuchet ms", 19, bold=True)
        self._fonte_hud_p    = pygame.font.SysFont("trebuchet ms", 14)
        self._fonte_status   = pygame.font.SysFont("trebuchet ms", 13, bold=True)
        self._fonte_prompt   = pygame.font.SysFont("trebuchet ms", 15, bold=True)
        self._fonte_cadeado  = pygame.font.SysFont("trebuchet ms", 20, bold=True)
        self._fonte_hotbar_simbolo = pygame.font.SysFont("trebuchet ms", 17, bold=True)
        self._fonte_hotbar_qtd     = pygame.font.SysFont("trebuchet ms", 12, bold=True)
 
    def _configurar_estados(self):
        try:
            self.fsm.registrar("menu", EstadoMenuAdaptador(self.fsm))
            self.fsm.registrar("jogo", EstadoJogando(self.fsm))
            self.fsm.registrar("pause", EstadoPauseAdaptador(self.fsm))
            self.fsm.registrar("gameover", EstadoGameOverAdaptador(self.fsm))
            self.fsm.registrar("loja", EstadoLojaAdaptador(self.fsm))
            self.fsm.registrar("vitoria", EstadoVitoriaAdaptador(self.fsm))
            self.fsm.registrar("dialogo", None)
            self.fsm.mudar_estado_imediato("menu")
        except Exception as e:
            print(f"\n[ERRO CRÍTICO NA MÁQUINA DE ESTADOS]: {e}")
            import traceback
            traceback.print_exc()
            pygame.quit()
            sys.exit()
 
    def _resetar_jogo(self):
        self.player, self.inventario, self.fase_atual, self.rodando = Player(), Inventario(), FASE_INICIAL, True
        self._carregar_fase(primeiro_spawn=True)
 
    def _carregar_fase(self, primeiro_spawn=False):
        self.bombas, self.projeteis, self.itens_chao, self.npcs, self.saida_rect, self.saida_aberta = [], [], [], [], None, False
        self.mapa = self.gerador.gerar_fase(self.fase_atual)
        self.saida_rect = None
        for lin, linha in enumerate(self.mapa):
            for col, tile in enumerate(linha):
                if tile == 3:
                    self.saida_rect = pygame.Rect(col * TELA_SIZE, lin * TELA_SIZE, TELA_SIZE, TELA_SIZE)
                    break
            if self.saida_rect:
                break
 
        if primeiro_spawn:
            self.player.rect.topleft = (TELA_SIZE + 5, TELA_SIZE + 5)
            self.player.sincronizar_posicao()
        else:
            livres = self.gerador.listar_chao_livre_acessivel(self.mapa)
            lin, col = random.choice(livres) if livres else (1, 1)
            self.player.rect.topleft = (col * TELA_SIZE + 5, lin * TELA_SIZE + 5)
            self.player.sincronizar_posicao()
 
        self._cache_paredes_fisicas()
        self._spawnar_inimigos()
 
    def _cache_paredes_fisicas(self):
        self.paredes = []
        self.paredes_projeteis = []

        for lin_idx, linha in enumerate(self.mapa):
            for col_idx, tile in enumerate(linha):
                if tile in (1, 2, 4, 5):
                    parede = pygame.Rect(
                        col_idx * TELA_SIZE,
                        lin_idx * TELA_SIZE,
                        TELA_SIZE,
                        TELA_SIZE,
                    )
                    self.paredes.append(parede)
                    if tile != 5:
                        self.paredes_projeteis.append(parede)
 
    def _spawnar_inimigos(self):
        self.inimigos = []
        origem_lin = self.player.rect.centery // TELA_SIZE
        origem_col = self.player.rect.centerx // TELA_SIZE
        candidatos = self.gerador.listar_chao_livre_acessivel(
            self.mapa,
            excluir_raio=5,
            origem=(origem_lin, origem_col),
        )
        random.shuffle(candidatos)

        legiao_atual = []
        for classe, qtd_min, qtd_max in _tabela_spawns(self.fase_atual):
            quantidade = random.randint(qtd_min, qtd_max)
            criados = 0

            while candidatos and criados < quantidade:
                lin, col = candidatos.pop()
                x, y = col * TELA_SIZE, lin * TELA_SIZE

                if classe is LegiaoDeFantasmas:
                    mob = LegiaoDeFantasmas(x, y, grupo=legiao_atual)
                else:
                    mob = classe(x, y)

                colide = any(mob.rect.colliderect(parede) for parede in self.paredes)
                colide = colide or any(mob.rect.colliderect(outro.rect) for outro in self.inimigos)
                if colide:
                    continue

                self.inimigos.append(mob)
                if isinstance(mob, LegiaoDeFantasmas):
                    legiao_atual.append(mob)
                criados += 1

    def _gerar_drops_inimigo(self, inimigo):
        if getattr(inimigo, "_drops_gerados", False):
            return

        inimigo._drops_gerados = True
        if isinstance(inimigo, Slime) and inimigo.dividiu:
            return

        tocar('morte')
        self.itens_chao.extend(gerar_drops_mob(inimigo))

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
            if b.explodiu and b.efeito_timer <= 0:
                self.bombas.remove(b)
                self._cache_paredes_fisicas()
 
        for inimigo in self.inimigos:
            if not inimigo.ativo:
                self._gerar_drops_inimigo(inimigo)

        self.inimigos = [i for i in self.inimigos if i.ativo]
        novos_slimes, hitbox_picareta = [], self.player.hitbox_picareta_atual()
 
        for inimigo in self.inimigos:
            inimigo.mover(self.player, self.paredes, self.mapa, self.bombas)
 
            if hasattr(inimigo, 'projeteis_pendentes') and inimigo.projeteis_pendentes:
                tocar('projetil')
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
            if isinstance(inimigo, Boss):
                ataques_antes = {id(ataque) for ataque in inimigo.ataques_ativos}
                inimigo.atualizar_ataques(self.player, self.paredes, self.mapa)
                if any(id(ataque) not in ataques_antes for ataque in inimigo.ataques_ativos):
                    tocar('aviso_ataque')
 
            if hitbox_picareta and not inimigo._atingindo_esse_swing and inimigo.rect.colliderect(hitbox_picareta):
                inimigo._atingindo_esse_swing = True
                dano = self.player.dano_picareta_para(inimigo)
                if isinstance(inimigo, Slime):
                    dividiu = inimigo.receber_dano_picareta(dano, self.player.rect)
                    if dividiu:
                        for _ in range(2):
                            mini = Slime(inimigo.rect.x, inimigo.rect.y, mini=True)
                            mini._atingindo_esse_swing = True
                            novos_slimes.append(mini)
                else: inimigo.receber_dano_picareta(dano, self.player.rect)
 
            if not hitbox_picareta:
                inimigo._atingindo_esse_swing = False
            if not inimigo.ativo:
                self._gerar_drops_inimigo(inimigo)
 
            # golem de lava: ataque especial de solo a distancia, roda todo frame
            # (o cooldown/alcance interno dele decide quando realmente bate)
            if isinstance(inimigo, GolemLava):
                avisava_antes = inimigo.avisando_ataque
                inimigo.atacar_solo(self.player)
                if inimigo.avisando_ataque and not avisava_antes:
                    tocar('aviso_ataque')
 
            if isinstance(inimigo, Golem): inimigo.aplicar_knockback_no_player(self.player, self.paredes, self.bombas)
            elif inimigo.rect.colliderect(self.player.rect): self.player.receber_dano()
 
        for s in novos_slimes: self.inimigos.append(s)
        for proj in self.projeteis[:]:
            proj.atualizar(self.player, self.paredes_projeteis)
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
            if self.fase_atual >= FASE_FINAL:
                self.fsm.mudar_estado("vitoria")
                return

            self.fase_atual += 1
            self._carregar_fase(primeiro_spawn=False)
            self.fsm.mudar_estado("jogo")
            return
 
        if self.player.hp <= 0: self.fsm.mudar_estado("gameover")
        self._atualizar_camera()
 
    def _desenhar_jogo(self):
        self.desenhar_cenario()
        for b in self.bombas:
            b.desenhar(self.tela, self.cam_x, self.cam_y)
        for item in self.itens_chao: item.desenhar(self.tela, self.cam_x, self.cam_y)
        for proj in self.projeteis: proj.desenhar(self.tela, self.cam_x, self.cam_y)
        for npc in self.npcs: npc.desenhar(self.tela, self.cam_x, self.cam_y)
 
        for inimigo in self.inimigos:
            inimigo.desenhar(self.tela, self.cam_x, self.cam_y)

            if isinstance(inimigo, Boss):
                inimigo.desenhar_extra(self.tela, self.cam_x, self.cam_y)
                inimigo.desenhar_ataques(self.tela, self.cam_x, self.cam_y)
 
        self.player.desenhar(self.tela, self.cam_x, self.cam_y)
 
        self.player.desenhar_picareta(self.tela, self.cam_x, self.cam_y)
        self._desenhar_prompt_npc()
        self.desenhar_hud()
 
    def desenhar_cenario(self):
        bioma = _bioma(self.fase_atual)
        cores = BIOMAS[bioma]
        carregadores_sprites = {
            1: (_carregar_sprites_bioma1, _sprite_bioma1),
            2: (_carregar_sprites_bioma2, _sprite_bioma2),
            3: (_carregar_sprites_bioma3, _sprite_bioma3),
        }
        carregar_sprites, obter_sprite = carregadores_sprites.get(bioma, (None, None))
        usar_sprites = carregar_sprites is not None and bool(carregar_sprites())
        self.tela.fill(cores['chao'])

        linha_inicio = max(0, self.cam_y // TELA_SIZE)
        linha_fim = min(len(self.mapa), (self.cam_y + ALTURA) // TELA_SIZE + 1)
        coluna_inicio = max(0, self.cam_x // TELA_SIZE)
        coluna_fim = min(len(self.mapa[0]), (self.cam_x + LARGURA) // TELA_SIZE + 1)

        for lin_idx in range(linha_inicio, linha_fim):
            inline = self.mapa[lin_idx]
            for col_idx in range(coluna_inicio, coluna_fim):
                tile = inline[col_idx]
                x = col_idx * TELA_SIZE - self.cam_x
                y = lin_idx * TELA_SIZE - self.cam_y
                rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)

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
                    sprite = obter_sprite(tipo, lin_idx, col_idx, animado=False) if tipo else None
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
        fonte, fonte_p = self._fonte_hud, self._fonte_hud_p

        # Vida: painel discreto com barra preenchida, sem contorno branco forte.
        bx, by, bl, ba = 18, ALTURA - 58, 230, 25
        pygame.draw.rect(self.tela, (25, 21, 18), (bx - 7, by - 7, bl + 14, ba + 14), border_radius=8)
        pygame.draw.rect(self.tela, (75, 39, 34), (bx, by, bl, ba), border_radius=5)
        fw = max(0, int(bl * self.player.hp_pct))
        if fw > 0:
            cor_vida = (int(190 * (1 - self.player.hp_pct) + 45), int(100 + 105 * self.player.hp_pct), 65)
            pygame.draw.rect(self.tela, cor_vida, (bx, by, fw, ba), border_radius=5)
        pygame.draw.rect(self.tela, (125, 105, 83), (bx, by, bl, ba), 1, border_radius=5)
        hp_txt = fonte_p.render(f'VIDA  {self.player.hp}/{self.player.hp_max}', True, (245, 235, 215))
        self.tela.blit(hp_txt, (bx + 8, by + 4))

        status_y = by - 23
        if not self.player.imune_veneno and self.player._veneno_timer > 0:
            self.tela.blit(fonte_p.render('Envenenado', True, (157, 205, 105)), (bx, status_y))
            status_y -= 18
        if self.player._fogo_timer > 0:
            self.tela.blit(fonte_p.render('Em chamas', True, (226, 133, 76)), (bx, status_y))

        # Ações ficam em pequenas etiquetas em vez de texto solto na parte inferior.
        def etiqueta(x, texto, cor):
            imagem = fonte.render(texto, True, cor)
            caixa = pygame.Rect(x, ALTURA - 53, imagem.get_width() + 22, 32)
            pygame.draw.rect(self.tela, (27, 24, 20), caixa, border_radius=6)
            pygame.draw.rect(self.tela, (89, 73, 54), caixa, 1, border_radius=6)
            self.tela.blit(imagem, (caixa.x + 11, caixa.y + 6))

        texto_bomba = f'Botão direito  ·  {self.player.bomba_cooldown/60:.1f}s' if self.player.bomba_cooldown > 0 else 'Botão direito  ·  Bomba'
        texto_picareta = f'Botão esquerdo  ·  {self.player.picareta_cooldown/60:.1f}s' if self.player.picareta_cooldown > 0 else 'Botão esquerdo  ·  Picareta'
        etiqueta(275, texto_bomba, (220, 177, 105) if self.player.bomba_cooldown > 0 else (177, 202, 137))
        etiqueta(520, texto_picareta, (190, 171, 125))

        nomes = {1: 'Caverna Normal', 2: 'Caverna Escura', 3: 'Caverna de Fungos', 4: 'Caverna de Cristais', 5: 'Núcleo Vulcânico'}
        fase = fonte.render(f'FASE {self.fase_atual}  ·  {nomes[_bioma(self.fase_atual)]}', True, (232, 215, 179))
        fase_caixa = pygame.Rect(LARGURA // 2 - fase.get_width() // 2 - 13, 9, fase.get_width() + 26, 31)
        pygame.draw.rect(self.tela, (28, 25, 21), fase_caixa, border_radius=6)
        pygame.draw.rect(self.tela, (91, 75, 53), fase_caixa, 1, border_radius=6)
        self.tela.blit(fase, (fase_caixa.x + 13, fase_caixa.y + 6))

        if self.saida_aberta:
            aviso = fonte_p.render('Saída aberta  ·  aproxime-se do NPC e aperte E', True, (163, 211, 133))
            self.tela.blit(aviso, aviso.get_rect(center=(LARGURA // 2, 52)))
        inimigos = fonte_p.render(f'{len(self.inimigos)} inimigos', True, (220, 139, 115) if self.inimigos else (155, 190, 135))
        self.tela.blit(inimigos, (LARGURA - inimigos.get_width() - 20, 17))
        self._desenhar_barra_status()
        self._desenhar_barra_boss()
        self._desenhar_inventario_hud()

    def _desenhar_barra_status(self):
        fonte, p = self._fonte_status, self.player
        items = [
            ('Picareta', p.nivel_forca, 5),
            ('Velocidade', p.nivel_velocidade, 4),
            ('Vida extra', p.nivel_hp, 5),
            ('Alcance bomba', p.nivel_bomba_alcance, 3),
            ('Pavio', p.nivel_bomba_cd, 3),
            ('Escudo', p.nivel_escudo, 3),
        ]
        sx, sy = 18, 78
        for label, nivel, maximo in items:
            texto = fonte.render(label, True, (180, 166, 142))
            self.tela.blit(texto, (sx, sy))
            barra_x = sx + 112
            for indice in range(maximo):
                cor = (183, 132, 76) if indice < nivel else (54, 47, 39)
                pygame.draw.rect(self.tela, cor, (barra_x + indice * 13, sy + 3, 9, 9), border_radius=2)
            sy += 21
        if p.escudo_cargas > 0:
            escudo = fonte.render(f'Escudo disponível: {p.escudo_cargas}', True, (139, 194, 205))
            self.tela.blit(escudo, (sx, sy + 2))

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
        self.tela_vitoria.tela  = self.tela
 
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
