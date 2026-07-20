import pygame
 
class EstadoGame:
    """Classe base para todos os estados (telas) do jogo."""
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
 
    def iniciar(self):
        pass
 
    def handle_event(self, event):
        pass
 
    def atualizar(self):
        pass
 
    def desenhar(self, tela):
        pass
 
 
class TransicaoFade:
    """Gerencia efeitos visuais de transição (escurecer/clarear tela)."""
    def __init__(self, velocidade=8):
        self.velocidade = velocidade
        self.alpha = 0
        self.modo = None  # 'out' (escurecendo), 'in' (clareando)
        self.proximo_estado = None
 
    def iniciar(self, proximo_estado):
        self.proximo_estado = proximo_estado
        self.modo = 'out'
        self.alpha = 0
 
    def atualizar(self, gerenciador):
        if self.modo == 'out':
            self.alpha += self.velocidade
            if self.alpha >= 255:
                self.alpha = 255
                gerenciador.mudar_estado_imediato(self.proximo_estado)
                self.modo = 'in'
        elif self.modo == 'in':
            self.alpha -= self.velocidade
            if self.alpha <= 0:
                self.alpha = 0
                self.modo = None
                self.proximo_estado = None
 
    def desenhar(self, tela):
        if self.modo is not None:
            fade_surf = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
            fade_surf.fill((12, 10, 18, self.alpha))
            tela.blit(fade_surf, (0, 0))
    
