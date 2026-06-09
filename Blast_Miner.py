import pygame
import random

from Mapas.gerador_mapas import GeradorProcedural
from entidades.Player import Player
from entidades.Fantasma import Fantasma
from entidades.Golem import Golem
from objetos.Bomba import Bomba
from telas.tela_inicial import TelaInicial
from telas.tela_jogo import TelaPause
from telas.tela_gameover import TelaGameOver



#configs da janela
ALTURA = 900
LARGURA = 1200
TELA_SIZE = 50

class BlastMiner:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Blast Miner Co. - IFRN")
        self.sprites = {
            "chao": pygame.transform.scale(pygame.image.load("assets/chao.png"), (TELA_SIZE, TELA_SIZE)),
            "parede": pygame.transform.scale(pygame.image.load("assets/parede.png"), (TELA_SIZE, TELA_SIZE)),
            "minerio": pygame.transform.scale(pygame.image.load("assets/minerio.png"), (TELA_SIZE, TELA_SIZE)) 
        }

        self.clock  = pygame.time.Clock()
        
        self.player = Player()
        self.fase_atual = 1
        self.mapa = MAPA_FASE_1
        self.inimigos = [
            Fantasma(850, 700),
            Golem(600, 450),
        ]
        self.rodando    = True
        self.paredes    = []
        self.bombas     = []
        self.saida_rect = None

        self.estado        = "menu"
        self.tela_inicial  = TelaInicial(self.tela)
        self.tela_pause    = TelaPause(self.tela)
        self.tela_gameover = TelaGameOver(self.tela)

    # ──────────────────────────────────────────────────────────────────────
    def _resetar_jogo(self):
        self.player     = Player()
        self.fase_atual = 1
        self.mapa       = MAPA_FASE_1
        self.inimigos   = [
            Fantasma(850, 700),
            Golem(600, 450),
        ]
        self.paredes    = []
        self.bombas     = []
        self.saida_rect = None

    # ──────────────────────────────────────────────────────────────────────
    def desenhar_cenario(self):
        self.paredes = []
        for linha_idx, linha in enumerate(self.mapa_atual):
            for col_idx, tile in enumerate(linha):
                x = col_idx * TELA_SIZE
                y = linha_idx * TELA_SIZE

                if tile == 0:
                    self.tela.blit(self.sprites["chao"], (x, y))
                elif tile == 1:
                    rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
                    self.tela.blit(self.sprites["parede"], (x, y))
                    self.paredes.append(rect)
                elif tile == 2:
                    rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
                    self.tela.blit(self.sprites["minerio"], (x,y))
                    self.paredes.append(rect)
                elif tile == 4:
                    rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
                    pygame.draw.rect(self.tela, (139, 69, 19), rect)
                    pygame.draw.circle(self.tela, (255, 215, 0), (x + 25, y + 25), 10)  
                    self.paredes.append(rect)
                elif tile == 3:
                    self.saida_rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
                    pygame.draw.rect(self.tela, (150, 0, 0), self.saida_rect)
                

    def desenhar_hud(self):
        fonte = pygame.font.SysFont("monospace", 22, bold=True)

        texto_vida = fonte.render(f"VIDA: {'❤ ' * self.player.vida}", True, (255, 80, 80))
        self.tela.blit(texto_vida, (10, ALTURA - 40))

        if self.player.bomba_cooldown > 0:
            segundos    = self.player.bomba_cooldown / 60
            texto_bomba = fonte.render(f"BOMBA: {segundos:.1f}s", True, (255, 200, 0))
        else:
            texto_bomba = fonte.render("BOMBA: PRONTA", True, (100, 255, 100))
        self.tela.blit(texto_bomba, (200, ALTURA - 40))

    # ──────────────────────────────────────────────────────────────────────
    def _logica_jogo(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.estado = "pause"
                    return

                if event.key == pygame.K_SPACE:
                    if self.player.pode_plantar_bomba():
                        col = self.player.rect.centerx // 50
                        lin = self.player.rect.centery // 50
                        nova_bomba = Bomba(col * 50, lin * 50)
                        self.bombas.append(nova_bomba)
                        self.player.plantar_bomba()

        self.player.controlar(self.paredes, self.bombas)
        if self.player.invencivel_timer > 0:
            self.player.invencivel_timer -= 1

        for b in self.bombas[:]:
            b.atualizar(self.mapa, self.player, self.inimigos)
            if b.explodiu:
                self.bombas.remove(b)

        self.inimigos = [i for i in self.inimigos if i.ativo]

        for inimigo in self.inimigos:
            inimigo.mover(self.player, self.paredes, self.mapa)

            if isinstance(inimigo, Golem):
                inimigo.aplicar_knockback_no_player(self.player, self.paredes, self.bombas)
            elif inimigo.rect.colliderect(self.player.rect):
                self.player.receber_dano()

        # Game Over
        if self.player.vida <= 0:
            self.estado = "gameover"
            return

        # Vitória / próxima fase
        if self.saida_rect and self.player.rect.colliderect(self.saida_rect):
            if self.fase_atual == 1:
                self.fase_atual = 2
                self.mapa = MAPA_FASE_2
                self.player.rect.topleft = (50, 50)
                self.saida_rect = None
                self.inimigos = [
                    Fantasma(100, 100),
                    Golem(300, 200),
                ]
            else:
                print("=== CONTRATO CUMPRIDO — VOCÊ ESCAPOU! ===")
                self.estado = "menu"
                self._resetar_jogo()

    def _desenhar_jogo(self):
        self.tela.fill((20, 20, 20))
        self.desenhar_cenario()

        for b in self.bombas:
            pygame.draw.rect(self.tela, b.cor, b.rect)

        for inimigo in self.inimigos:
            inimigo.desenhar(self.tela)

        if self.player.invencivel_timer % 4 == 0:
            pygame.draw.rect(self.tela, (255, 200, 0), self.player.rect)

        self.desenhar_hud()
        # sem display.flip() aqui — fica no executar()

    # ──────────────────────────────────────────────────────────────────────
    def executar(self):
        while self.rodando:
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.rodando = False

                if self.estado == "menu":
                    acao = self.tela_inicial.handle_event(event)
                    if acao == "JOGAR":
                        self.estado = "jogo"
                    elif acao == "SAIR":
                        self.rodando = False

                elif self.estado == "pause":
                    acao = self.tela_pause.handle_event(event)
                    if acao == "CONTINUAR":
                        self.estado = "jogo"
                    elif acao == "MENU PRINCIPAL":
                        self.estado = "menu"
                        self._resetar_jogo()
                    elif acao == "SAIR":
                        self.rodando = False

                elif self.estado == "gameover":
                    acao = self.tela_gameover.handle_event(event)
                    if acao == "TENTAR NOVAMENTE":
                        self._resetar_jogo()
                        self.estado = "jogo"
                    elif acao == "MENU PRINCIPAL":
                        self._resetar_jogo()
                        self.estado = "menu"
                    elif acao == "SAIR":
                        self.rodando = False

            # ── desenho / lógica por estado ───────────────────────────────
            if self.estado == "menu":
                self.tela_inicial.draw()

            elif self.estado == "jogo":
                self._logica_jogo(events)
                if self.estado == "jogo":
                    self._desenhar_jogo()
                    pygame.display.flip()

            elif self.estado == "pause":
                self._desenhar_jogo()
                self.tela_pause.draw()  # já tem flip interno

            elif self.estado == "gameover":
                self.tela_gameover.draw()

            self.clock.tick(60)

        pygame.quit()
