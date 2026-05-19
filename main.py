import pygame
from classes import Player, Bomba, Fantasma, Golem

# Configurações de Tela
ALTURA     = 900
LARGURA    = 1200
TELA_SIZE  = 50

# Matriz do Mapa (0:chão, 1:parede, 2:minério, 3:saída)
MAPA_FASE_1 = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 2, 1, 0, 1, 2, 1, 2, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 2, 1, 1],
    [1, 0, 2, 0, 2, 2, 0, 2, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 2, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 1],
    [1, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 1],
    [1, 2, 2, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 1],
    [1, 2, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 2, 2, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 2, 1, 1],
    [1, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 1, 2, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 3, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


class BlastMiner:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Blast Miner Co. - IFRN")

        self.clock  = pygame.time.Clock()
        self.player = Player()
        self.inimigos = [
            Fantasma(850, 700),   # Inimigo tipo Fantasma
            Golem(600, 400),      # Inimigo tipo Golem
        ]
        self.rodando   = True
        self.paredes   = []
        self.bombas    = []
        self.saida_rect = None

    def desenhar_cenario(self):
        self.paredes = []
        for linha_idx, linha in enumerate(MAPA_FASE_1):
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
                        if self.player.pode_plantar_bomba():
                            col = self.player.rect.centerx // 50
                            lin = self.player.rect.centery // 50
                            nova_bomba = Bomba(col * 50, lin * 50)
                            self.bombas.append(nova_bomba)
                            self.player.plantar_bomba()

            # --- LÓGICA ---

            # Player
            self.player.controlar(self.paredes, self.bombas)
            if self.player.invencivel_timer > 0:
                self.player.invencivel_timer -= 1

            # Bombas
            for b in self.bombas[:]:
                b.atualizar(MAPA_FASE_1, self.player, self.inimigos)
                if b.explodiu:
                    self.bombas.remove(b)

            # Inimigos remove os que foram eliminados
            self.inimigos = [i for i in self.inimigos if i.ativo]

            for inimigo in self.inimigos:
                inimigo.mover(self.player, self.paredes, MAPA_FASE_1)

                # Golem causa knockback; Fantasma só causa dano normal
                if isinstance(inimigo, Golem):
                    inimigo.aplicar_knockback_no_player(self.player)
                elif inimigo.rect.colliderect(self.player.rect):
                    self.player.receber_dano()

            # Game Over
            if self.player.vida <= 0:
                print("=== CONTRATO RESCINDIDO — GAME OVER ===")
                self.rodando = False

            # Vitória
            if self.saida_rect and self.player.rect.colliderect(self.saida_rect):
                print("=== CONTRATO CUMPRIDO — VOCÊ ESCAPOU! ===")
                self.rodando = False

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
    game = BlastMiner()
    game.executar()
