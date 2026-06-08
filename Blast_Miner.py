import pygame
import random

from Mapas.gerador_mapas import GeradorProcedural
from entidades.Player import Player
from entidades.Fantasma import Fantasma
from entidades.Golem import Golem
from objetos.Bomba import Bomba


#configs da janela
ALTURA = 900
LARGURA = 1200
TELA_SIZE = 50

class BlastMiner:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Blast Miner Co. - IFRN")

        self.clock  = pygame.time.Clock()
        
        self.player = Player()
        
        #adiçao da criaçao do mapa procedural
        self.gerador = GeradorProcedural()

        self.mapa_atual = self.gerador.gerar_fase()      

        self.inimigos = []
        self.spawnar_inimigos_procedural()

        self.rodando   = True
        self.paredes   = []
        self.bombas    = []
        self.saida_rect = None

    def spawnar_inimigos_procedural(self):
        #spawna os inimigos longe do mike e somente no chão (0)
        self.inimigos = []
        #sorteia a quantidade de inimigos 
        quantidade_inimigos = random.randint(2, 4)

        while len(self.inimigos) < quantidade_inimigos:
            l = random.randint(1, len(self.mapa_atual) -2)
            c = random.randint(6, len(self.mapa_atual[0]) - 2)
            if self.mapa_atual[l][c] == 0:  #somente no chão
                x = c * TELA_SIZE
                y = l * TELA_SIZE
                self.inimigos.append(Fantasma(x, y))
              
    def desenhar_cenario(self):
        self.paredes = []
        for linha_idx, linha in enumerate(self.mapa_atual):
            for col_idx, tile in enumerate(linha):
                x = col_idx * TELA_SIZE
                y = linha_idx * TELA_SIZE

                if tile == 0:
                    cor = (35, 35, 35) if (linha_idx + col_idx) % 2 == 0 else (45, 45, 45)
                    pygame.draw.rect(self.tela, cor, (x, y, TELA_SIZE, TELA_SIZE))
                elif tile == 1:
                    rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
                    pygame.draw.rect(self.tela, (60, 60, 75), rect)
                    self.paredes.append(rect)
                elif tile == 2:
                    rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
                    pygame.draw.rect(self.tela, (100, 50, 20), rect)
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
        """Exibe a vida do player e o cooldown da bomba na tela."""
        fonte = pygame.font.SysFont("monospace", 22, bold=True)

        # Vida
        texto_vida = fonte.render(f"VIDA: {'❤ ' * self.player.vida}", True, (255, 80, 80))
        self.tela.blit(texto_vida, (10, ALTURA - 40))

        # Cooldown da bomba
        if self.player.bomba_cooldown > 0:
            segundos = self.player.bomba_cooldown / 60
            texto_bomba = fonte.render(f"BOMBA: {segundos:.1f}s", True, (255, 200, 0))
        else:
            texto_bomba = fonte.render("BOMBA: PRONTA", True, (100, 255, 100))
        self.tela.blit(texto_bomba, (200, ALTURA - 40))

    def executar(self):
        while self.rodando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Só planta bomba se o cooldown permitir
                        if self.player.pode_plantar_bomba() and len(self.bombas) < 1:  # Limite de bombas ativas
                            col = self.player.rect.centerx // 50
                            lin = self.player.rect.centery // 50
                            nova_bomba = Bomba(col * 50, lin * 50)
                            self.bombas.append(nova_bomba)

            # Player
            self.player.controlar(self.paredes, self.bombas)
            if self.player.invencivel_timer > 0:
                self.player.invencivel_timer -= 1   

            # Bombas
            for b in self.bombas[:]:
                b.atualizar(self.mapa_atual, self.player, self.inimigos)
                if b.explodiu:
                    self.bombas.remove(b)

            # Inimigos remove os que foram eliminados
            self.inimigos = [i for i in self.inimigos if i.ativo]

            for inimigo in self.inimigos:
                inimigo.mover(self.player, self.paredes, self.mapa_atual)

                # Golem causa knockback; Fantasma só causa dano normal
                if isinstance(inimigo, Golem):
                    inimigo.aplicar_knockback_no_player(self.player, self.paredes, self.bombas)
                elif inimigo.rect.colliderect(self.player.rect):
                    self.player.receber_dano()

            # Game Over
            if self.player.vida <= 0:
                print("=== CONTRATO RESCINDIDO — GAME OVER ===")
                self.rodando = False

            # Vitória
            if self.saida_rect and self.player.rect.colliderect(self.saida_rect):
                print("=== PARABÉNS — VOCÊ ESCAPOU! PRÓXIMO NIVEL!!===")

                self.mapa_atual == self.gerador.gerar_fase()
                self.player.rect.topleft = (50, 50)
                self.saida_rect = None
                self.bombas = []
                self.spawnar_inimigos_procedural()

            # --- DESENHO ---
            self.tela.fill((20, 20, 20))
            self.desenhar_cenario()

            for b in self.bombas:
                pygame.draw.rect(self.tela, b.cor, b.rect)

            for inimigo in self.inimigos:
                inimigo.desenhar(self.tela)

            # Player pisca quando invencível
            if self.player.invencivel_timer % 4 == 0:
                pygame.draw.rect(self.tela, (255, 200, 0), self.player.rect)

            self.desenhar_hud()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    jogo = BlastMiner()
    jogo.executar()
