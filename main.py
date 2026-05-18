import pygame
from classes import Player, bomba, fantasma

ALTURA = 900 
LARGURA = 1200
TELA_SIZE = 50

# 0: chao, 1: parede, 2: minerio 3: saida
MAPA_FASE_1 = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 2, 1, 1],
    [1, 0, 2, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 2, 1, 2, 1, 2, 1, 2, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 1],
    [1, 2, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 1],
    [1, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 2, 1, 0, 1, 2, 1, 1],
    [1, 2, 2, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 1],
    [1, 2, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 2, 1, 1],
    [1, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 1, 0, 1, 2, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 2, 3, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

class BlastMiner:
    def __init__(self): 
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Blast Miner Co. - IFRN")
        
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.inimigos[fantasma(1200, 800)]
        self.rodando = True
        self.paredes = [] # lista de obstaculos
        self.bomba = [] # lista de bombas ativas
        self.saida_rect = None

    def desenhar_cenario(self):
        """ transforma os numeros da matriz em desenhos na tela """
        self.paredes = [] 
        for linha_idx, linha in enumerate(MAPA_FASE_1):
            for col_idx, tile in enumerate(linha):
                x = col_idx * TELA_SIZE
                y = linha_idx * TELA_SIZE

                if tile == 0: # chao
                    cor = (35, 35, 35) if (linha_idx + col_idx) % 2 == 0 else (45, 45, 45)
                    pygame.draw.rect(self.tela, cor, (x, y, TELA_SIZE, TELA_SIZE))
                
                elif tile == 1: # parede inquebravel
                    rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
                    pygame.draw.rect(self.tela, (60, 60, 75), rect)
                    self.paredes.append(rect) # adiciona a colisão
                
                elif tile == 2: # parede destrutivel 
                    rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
                    pygame.draw.rect(self.tela, (100, 50, 20), rect)
                    self.paredes.append(rect) # tambem bloqueia o player
                
                elif tile == 3: # saida
                    self.saida_rect = pygame.Rect(x, y, TELA_SIZE, TELA_SIZE)
                    pygame.draw.rect(self.tela, (150, 0, 0), self.saida_rect)

    def executar(self):
        while self.rodando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando = False
                if event.type == pygame.KEYDOWN:
                    col = self.player.rect.centerx // 50
                    lin = self.player.rect.centery // 50
                    
                    pos_x = col * 50
                    pos_y = lin * 50
                    if event.key == pygame.K_SPACE:
                        nova_bomba = bomba(pos_x, pos_y)
                        self.bomba.append(nova_bomba)


            # logica
            self.player.controlar(self.paredes)

            #bomba
            for b in self.bomba[:]:
                b.atualizar(MAPA_FASE_1, self.player)
                if b.explodiu:
                    self.bomba.remove(b)

            #fantasma
            for inimigo in self.inimigos:
                inimigo.mover(self.player)
                if inimigo.rect.colliderect(self.player.rect):
                    self.player.receber_dano()

            # vitoria
            if self.saida_rect and self.player.rect.colliderect(self.saida_rect):
                print("Você achou a saída!")
                self.rodando = False

            # desenho
            self.tela.fill((20, 20, 20)) # limpa fundo
            self.desenhar_cenario() # desenha o mapa
            

            for b in self.bomba:
                pygame.draw.rect(self.tela, b.cor, b.rect) # desenha as bombas

            # fantasma
            for inimigo in self.inimigos:
                pygame.draw.rect(self.tela, (255, 0, 0), inimigo.rect)

            
            # player
            pygame.draw.rect(self.tela, (255, 200, 0), self.player.rect)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = BlastMiner()
    game.executar()