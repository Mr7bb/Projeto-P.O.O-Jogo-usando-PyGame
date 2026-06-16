import pygame

class Inimigo:
    def __init__(self, x, y, largura, altura, velocidade, vida, cor):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.velocidade = velocidade
        self.vida = vida
        self.cor = cor
        self.ativo = True         

        self.kb_dx = 0
        self.kb_dy = 0
        self.kb_timer = 0

        self._atingindo_esse_swing = False


    def receber_dano_explosao(self):
        self.vida -= 1
        print(f"[{self.__class__.__name__}] Atingido! Vida restante: {self.vida}")
        if self.vida <= 0:
            self.ativo = False
            print(f"[{self.__class__.__name__}] Eliminado!")
    
    def receber_dano_espada(self, dano, player_rect):
        """Aplica dano e empurra o inimigo para longe do player."""
        self.vida -= dano
        print(f"[{self.__class__.__name__}] Atingido pela espada! Vida: {self.vida}")

        # Calcula a direção do empurrão (para longe do player)
        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        forca = 6
        self.kb_dx    = (dx / dist) * forca
        self.kb_dy    = (dy / dist) * forca
        self.kb_timer = 8   # dura 8 frames

        if self.vida <= 0:
            self.ativo = False
            print(f"[{self.__class__.__name__}] Eliminado pela espada!")

    def _aplicar_knockback_proprio(self, paredes):
        """
        Chame no início do mover() de cada subclasse.
        Enquanto kb_timer > 0 o inimigo se move pelo empurrão
        e ignora a própria IA.
        """
        if self.kb_timer <= 0:
            return
        self.kb_timer -= 1
        pos_x = self.rect.x
        pos_y = self.rect.y

        self.rect.x += int(self.kb_dx)
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x = pos_x
                self.kb_dx  = 0
                break

        self.rect.y += int(self.kb_dy)
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.y = pos_y
                self.kb_dy  = 0
                break

    def mover(self, player, paredes):
        
        raise NotImplementedError("Subclasses devem implementar mover()")

    def desenhar(self, tela):
        
        pygame.draw.rect(tela, self.cor, self.rect)
