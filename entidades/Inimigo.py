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
    
    def receber_dano_picareta(self, dano, player_rect):
        """Aplica dano, empurra o inimigo e agora notifica subclasses (Efeito Legião)."""
        self.vida -= dano
        print(f"[{self.__class__.__name__}] Atingido pela picareta! Vida: {self.vida}")

        # Correção do sistema da Legião: Se for uma LegiaoDeFantasmas, ativa a fúria geral ao tomar dano físico
        if self.__class__.__name__ == "LegiaoDeFantasmas":
            # Chama o método de fúria compartilhada contido na própria subclasse
            self.alertar_toda_legiao()

        dx = self.rect.centerx - player_rect.centerx
        dy = self.rect.centery - player_rect.centery
        dist = max(1, (dx**2 + dy**2) ** 0.5)
        forca = 6
        self.kb_dx    = (dx / dist) * forca
        self.kb_dy    = (dy / dist) * forca
        self.kb_timer = 8   

        if self.vida <= 0:
            self.ativo = False
            print(f"[{self.__class__.__name__}] Eliminado pela picareta!")

    def _aplicar_knockback_proprio(self, paredes):
        if self.kb_timer <= 0: return False
        self.kb_timer -= 1
        pos_x, pos_y = self.rect.x, self.rect.y

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
        return True

    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)