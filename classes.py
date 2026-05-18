import pygame
import random

# classe player (personagem)
class Player: 
    def __init__(self): 
        self.rect = pygame.Rect(50, 50, 50, 50) # player de 35px para blocos de 50px
        self.velocidade = 5
        self.vida = 3
        self.invencive_timer = 0

    def controlar(self, paredes, bombas):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
        teclas = pygame.key.get_pressed()

        # eixo X
        if teclas[pygame.K_a]: self.rect.x -= self.velocidade
        if teclas[pygame.K_d]: self.rect.x += self.velocidade
        for p in paredes:
            if self.rect.colliderect(p): self.rect.x = pos_antiga_x
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.x = pos_antiga_x

        # eixo Y
        if teclas[pygame.K_w]: self.rect.y -= self.velocidade
        if teclas[pygame.K_s]: self.rect.y += self.velocidade
        for p in paredes:
            if self.rect.colliderect(p): self.rect.y = pos_antiga_y
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.y = pos_antiga_y

    def receber_dano(self):
        if self.invencivel_timer == 0:
            self.vida -= 1
            self.invencivel_timer = 60 # 1 segundo de proteção
            print(f"Player recebeu dano! Vida: {self.vida}")

class bomba:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.tempo_explosao = 90
        self.cor = (0, 0, 0)
        self.explodiu = False
        self.solida = False

    def atualizar(self, mapa, player, inimigos): # Recebe os dois argumentos
        # Lógica para a bomba virar um obstáculo sólido
        if not self.solida:
            if not self.rect.colliderect(player.rect):
                self.solida = True

        if self.tempo_explosao > 0:
            self.tempo_explosao -= 1
        else:
            if not self.explodiu:
                self.explodir(mapa, player, inimigos)

    def explodir(self, mapa, player, inimigos):
        self.explodiu = True
        
        

        # 1. Descobrir a posição da bomba na grade (Matriz)
        # Dividimos o centro da bomba pelo tamanho do tile (50)
        col = self.rect.centerx // 50
        lin = self.rect.centery // 50

        # 2. Definir o alcance (Centro, Cima, Baixo, Esquerda, Direita)
        alcance = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for d_lin, d_col in alcance:
            alvo_l = lin + d_lin
            alvo_c = col + d_col

            # Verifica se não estamos tentando acessar fora dos limites da lista
            if 0 <= alvo_l < len(mapa) and 0 <= alvo_c < len(mapa[0]):
                explosao_rect = pygame.Rect(alvo_c * 50, alvo_l * 50, 50, 50)
                
                # SE ATINGIR MINÉRIO (2), ELE SOME (0)
                if mapa[alvo_l][alvo_c] == 2:
                    mapa[alvo_l][alvo_c] = 0

                # Dano no Player
                if player.rect.colliderect(explosao_rect):
                    player.receber_dano()
                
                # Dano nos Inimigos (Ativa fúria)
                for inimigo in inimigos:
                    if inimigo.rect.colliderect(explosao_rect):
                        inimigo.atravessar_paredes_furia()

    
    def atualizar_alcance(self, mapa, player):
        pass

class fantasma:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 45, 45)
        self.velocidade = 2
        self.cor = (255, 255, 255)
        self.vida = 3
        self.atravesar_timer = 0
        self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
        self.contador_passos = 0

    def mover(self, player, paredes):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
        # MODO FÚRIA: Persegue o player e ignora paredes
        if self.atravesar_timer > 0:
            self.atravesar_timer -= 1
            self.cor = (100, 100, 255) # Azul para indicar perigo
            
            if self.rect.x < player.rect.x: self.rect.x += self.velocidade
            elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade
            if self.rect.y < player.rect.y: self.rect.y += self.velocidade
            elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade
        
        # MODO NORMAL: Movimento aleatório e respeita paredes
        else:
            self.cor = (255, 225, 255)
            if self.direcao == 'cima': self.rect.y -= self.velocidade
            elif self.direcao == 'baixo': self.rect.y += self.velocidade
            elif self.direcao == 'esquerda': self.rect.x -= self.velocidade
            elif self.direcao == 'direita': self.rect.x += self.velocidade

            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x = pos_antiga_x
                    self.rect.y = pos_antiga_y
                    self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])

            self.contador_passos += 1
            if self.contador_passos > 60:
                self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                self.contador_passos = 0

    def atravessar_paredes_furia(self):
        if self.atravesar_timer <= 0: # Só ativa se não estiver em fúria
            self.vida -= 1
            self.atravesar_timer = 180 # 3 segundos de fúria
            print(f"Fantasma em fúria! Vida restante: {self.vida}")
    
    def morrer():
        pass