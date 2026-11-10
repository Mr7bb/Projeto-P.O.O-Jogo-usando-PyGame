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
        self._x_preciso = float(self.rect.x)
        self._y_preciso = float(self.rect.y)
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
 
    def salvar_posicao(self):
        return self._x_preciso, self._y_preciso

    def mover_x(self, deslocamento):
        self._x_preciso += deslocamento
        self.rect.x = round(self._x_preciso)

    def mover_y(self, deslocamento):
        self._y_preciso += deslocamento
        self.rect.y = round(self._y_preciso)

    def restaurar_x(self, x):
        self._x_preciso = float(x)
        self.rect.x = round(self._x_preciso)

    def restaurar_y(self, y):
        self._y_preciso = float(y)
        self.rect.y = round(self._y_preciso)

    def restaurar_posicao(self, x, y):
        self.restaurar_x(x)
        self.restaurar_y(y)

    def receber_dano_explosao(self, dano=2):
        # dano causado pela bomba. antes toda explosao tirava so 1 "hp" do mob, o que
        # deixava a bomba fraca de mais (pedido do Marquito pra melhorar isso um pouco,
        # sem virar arma de matar tudo num golpe so). agora tira 2 por padrao.
        self.vida -= dano
        print(f"[{self.__class__.__name__}] Atingido! Vida restante: {self.vida}")
        if self.vida <= 0:
            self.ativo = False
            print(f"[{self.__class__.__name__}] Eliminado!")
    
    def receber_dano_picareta(self, dano, player_rect):
        """aplica dano da picareta, empurra o inimigo pra longe do player e avisa a legiao se for fantasma."""
        self.vida -= dano
        print(f"[{self.__class__.__name__}] Atingido pela picareta! Vida: {self.vida}")
 
        alertar_legiao = getattr(self, "alertar_toda_legiao", None)
        if callable(alertar_legiao):
            alertar_legiao()
 
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
        if self.kb_timer <= 0:
            return False

        self.kb_timer -= 1
        pos_x, pos_y = self.salvar_posicao()

        self.mover_x(int(self.kb_dx))
        for parede in paredes:
            if self.rect.colliderect(parede):
                self.restaurar_x(pos_x)
                self.kb_dx = 0
                break

        self.mover_y(int(self.kb_dy))
        for parede in paredes:
            if self.rect.colliderect(parede):
                self.restaurar_y(pos_y)
                self.kb_dy = 0
                break

        return True

    def _patrulhar_aleatorio(self, paredes, passos_max=80):
        pos_antiga_x, pos_antiga_y = self.salvar_posicao()

        if self.direcao_patrulha == 'cima':
            self.mover_y(-self.velocidade)
        elif self.direcao_patrulha == 'baixo':
            self.mover_y(self.velocidade)
        elif self.direcao_patrulha == 'esquerda':
            self.mover_x(-self.velocidade)
        elif self.direcao_patrulha == 'direita':
            self.mover_x(self.velocidade)

        for parede in paredes:
            if self.rect.colliderect(parede):
                self.restaurar_posicao(pos_antiga_x, pos_antiga_y)
                self.direcao_patrulha = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                break

        self.passos_patrulha += 1
        if self.passos_patrulha > passos_max:
            self.direcao_patrulha = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
            self.passos_patrulha = 0

    def rect_na_tela(self, cam_x=0, cam_y=0):
        return pygame.Rect(
            self.rect.x - cam_x,
            self.rect.y - cam_y,
            self.rect.width,
            self.rect.height,
        )

    def desenhar(self, tela, cam_x=0, cam_y=0):
        pygame.draw.rect(tela, self.cor, self.rect_na_tela(cam_x, cam_y))
