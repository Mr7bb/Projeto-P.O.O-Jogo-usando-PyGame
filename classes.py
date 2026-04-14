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