import pygame

class Inimigo:
    def __init__(self, x, y, largura, altura, velocidade, vida, cor):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.velocidade = velocidade
        self.vida = vida
        self.cor = cor
        self.ativo = True           

    def receber_dano_explosao(self):
      
        self.vida -= 1
        print(f"[{self.__class__.__name__}] Atingido! Vida restante: {self.vida}")
        if self.vida <= 0:
            self.ativo = False
            print(f"[{self.__class__.__name__}] Eliminado!")

    def mover(self, player, paredes):
        
        raise NotImplementedError("Subclasses devem implementar mover()")

    def desenhar(self, tela):
        
        pygame.draw.rect(tela, self.cor, self.rect)
