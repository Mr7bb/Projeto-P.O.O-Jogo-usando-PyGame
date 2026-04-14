import pygame

# classe player (personagem)
class Player: 
    def __init__(self): 
        self.rect = pygame.Rect(50, 50, 50, 50) # player de 35px para blocos de 50px
        self.velocidade = 5

    def controlar(self, paredes):
        """ logica de 'Bate e Volta' para colisão """
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
        
        teclas = pygame.key.get_pressed()

        # eixo X
        if teclas[pygame.K_a]: self.rect.x -= self.velocidade
        if teclas[pygame.K_d]: self.rect.x += self.velocidade
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x = pos_antiga_x

        # eixo Y
        if teclas[pygame.K_w]: self.rect.y -= self.velocidade
        if teclas[pygame.K_s]: self.rect.y += self.velocidade
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.y = pos_antiga_y

# No arquivo classes.py

#APOLO QUE FEZ O CODIGO DA BOMBA

class bomba:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.tempo_explosao = 90
        self.cor = (0, 0, 0)
        self.explodiu = False
        self.dano = 3

    def colocar(self, player):
        # Centraliza a bomba no bloco onde o player está
        self.rect.x = player.rect.x
        self.rect.y = player.rect.y
        self.tempo_explosao = 90
        self.explodiu = False

    def atualizar(self, mapa, player): # Recebe os dois argumentos
        if self.tempo_explosao > 0:
            self.tempo_explosao -= 1
        else:
            if not self.explodiu:
                self.explodir(mapa, player) 

    def explodir(self, mapa, player):
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
                
                # SE ATINGIR MINÉRIO (2), ELE SOME (0)
                if mapa[alvo_l][alvo_c] == 2:
                    mapa[alvo_l][alvo_c] = 0