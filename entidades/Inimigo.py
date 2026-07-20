import pygame
import random
 
class Inimigo:
    """
    classe base de todo mundo que ataca o player (fantasma, goblin, slime, cogumelo, golem...).
    cada mob especifico herda daqui e sobrescreve o que precisar (tipo o mover, que cada um
    tem um jeito de andar diferente).
    """
 
    def __init__(self, x, y, largura, altura, velocidade, vida, cor):
        self.rect = pygame.Rect(x, y, largura, altura)
        self.velocidade = velocidade
        self.vida = vida
        self.cor = cor
        self.ativo = True         
 
        # essas 3 variaveis controlam o empurrao que o mob recebe quando toma dano
        self.kb_dx = 0
        self.kb_dy = 0
        self.kb_timer = 0
 
        # controla se esse mob ja foi atingido durante a espadada atual, pra nao tomar
        # dano varias vezes com um unico swing da picareta (ela fica ativa por alguns frames)
        self._atingindo_esse_swing = False
 
        # usado pelo metodo _patrulhar_aleatorio la embaixo. cada mob que usa patrulha
        # livre reaproveita essas duas variaveis (direcao atual e contador de passos)
        self.direcao_patrulha = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
        self.passos_patrulha = 0
 
    def receber_dano_explosao(self):
        # dano causado pela bomba. cada explosao tira 1 "hp" do mob
        self.vida -= 1
        print(f"[{self.__class__.__name__}] Atingido! Vida restante: {self.vida}")
        if self.vida <= 0:
            self.ativo = False
            print(f"[{self.__class__.__name__}] Eliminado!")
    
    def receber_dano_picareta(self, dano, player_rect):
        """aplica dano da picareta, empurra o inimigo pra longe do player e avisa a legiao se for fantasma."""
        self.vida -= dano
        print(f"[{self.__class__.__name__}] Atingido pela picareta! Vida: {self.vida}")
 
        # Correção do sistema da Legião: Se for uma LegiaoDeFantasmas, ativa a fúria geral ao tomar dano físico
        if self.__class__.__name__ == "LegiaoDeFantasmas":
            # Chama o método de fúria compartilhada contido na própria subclasse
            self.alertar_toda_legiao()
 
        # calcula a direcao do empurrao: sentido contrario de onde o player esta
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
        # empurra o mob pixel a pixel na direcao calculada em receber_dano_picareta,
        # cancelando o movimento se bater numa parede no meio do caminho.
        # retorna True enquanto o empurrao ainda ta rolando (quem chamar deve parar de
        # processar movimento normal nesse frame).
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
 
    def _patrulhar_aleatorio(self, paredes, passos_max=80):
        """
        movimento de patrulha generico: anda numa direcao aleatoria, e se bater numa parede
        ou andar passos_max passos sem bater em nada, escolhe uma direcao nova.
        golem, cogumelo agressivo e slime usavam essa mesma logica copiada e colada em cada
        arquivo, entao movi pra ca (classe mae) pra eles so chamarem esse metodo.
        """
        pos_antiga_x, pos_antiga_y = self.rect.x, self.rect.y
 
        if self.direcao_patrulha == 'cima':       self.rect.y -= self.velocidade
        elif self.direcao_patrulha == 'baixo':    self.rect.y += self.velocidade
        elif self.direcao_patrulha == 'esquerda': self.rect.x -= self.velocidade
        elif self.direcao_patrulha == 'direita':  self.rect.x += self.velocidade
 
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x, self.rect.y = pos_antiga_x, pos_antiga_y
                self.direcao_patrulha = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                break
 
        self.passos_patrulha += 1
        if self.passos_patrulha > passos_max:
            self.direcao_patrulha = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
            self.passos_patrulha = 0
 
    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
