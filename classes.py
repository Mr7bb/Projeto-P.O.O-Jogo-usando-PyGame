import pygame
import random

# CLASSE PLAYER

class Player:
    def __init__(self):
        self.rect = pygame.Rect(50, 50, 40, 40)  # 40x40 para não entalar nas paredes
        self.velocidade = 5
        self.vida = 3
        self.invencivel_timer = 0
        self.bomba_cooldown = 0       # Cooldown entre bombas (240 frames = 4 segundos)

    def controlar(self, paredes, bombas):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
        teclas = pygame.key.get_pressed()

        # Movimento X
        if teclas[pygame.K_a]: self.rect.x -= self.velocidade
        if teclas[pygame.K_d]: self.rect.x += self.velocidade
        for p in paredes:
            if self.rect.colliderect(p): self.rect.x = pos_antiga_x
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.x = pos_antiga_x

        # Movimento Y
        if teclas[pygame.K_w]: self.rect.y -= self.velocidade
        if teclas[pygame.K_s]: self.rect.y += self.velocidade
        for p in paredes:
            if self.rect.colliderect(p): self.rect.y = pos_antiga_y
        for b in bombas:
            if b.solida and self.rect.colliderect(b.rect): self.rect.y = pos_antiga_y

        # Atualiza cooldown da bomba
        if self.bomba_cooldown > 0:
            self.bomba_cooldown -= 1

    def pode_plantar_bomba(self):
        return self.bomba_cooldown == 0

    def plantar_bomba(self):
        self.bomba_cooldown = 240  # 4 segundos a 60fps

    def receber_dano(self):
        if self.invencivel_timer == 0:
            self.vida -= 1
            self.invencivel_timer = 60  # 1 segundo de proteção
            print(f"[MIKE] Recebeu dano! Vida: {self.vida}")

    def aplicar_knockback(self, origem_rect):
        """Empurra o player para longe de uma origem (usado pelo Golem)."""
        dx = self.rect.centerx - origem_rect.centerx
        dy = self.rect.centery - origem_rect.centery
        if dx != 0: self.rect.x += 40 * (1 if dx > 0 else -1)
        if dy != 0: self.rect.y += 40 * (1 if dy > 0 else -1)


# CLASSE BOMBA
class Bomba:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.tempo_explosao = 240   # 4 segundos a 60fps
        self.cor = (0, 0, 0)
        self.explodiu = False
        self.solida = False         # Vira sólida após o player sair de cima

    def atualizar(self, mapa, player, inimigos):
        # Lógica para a bomba virar um obstáculo sólido
        if not self.solida:
            if not self.rect.colliderect(player.rect):
                self.solida = True

        # Efeito visual: bomba pisca quando está prestes a explodir
        if self.tempo_explosao < 60:
            self.cor = (255, 0, 0) if (self.tempo_explosao // 8) % 2 == 0 else (200, 50, 50)
        else:
            self.cor = (20, 20, 20)

        if self.tempo_explosao > 0:
            self.tempo_explosao -= 1
        else:
            if not self.explodiu:
                self.explodir(mapa, player, inimigos)

    def explodir(self, mapa, player, inimigos):
        self.explodiu = True
        col = self.rect.centerx // 50
        lin = self.rect.centery // 50
        alcance = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]

        for d_lin, d_col in alcance:
            alvo_l = lin + d_lin
            alvo_c = col + d_col

            if 0 <= alvo_l < len(mapa) and 0 <= alvo_c < len(mapa[0]):
                explosao_rect = pygame.Rect(alvo_c * 50, alvo_l * 50, 50, 50)

                # Destruir minério
                if mapa[alvo_l][alvo_c] == 2:
                    mapa[alvo_l][alvo_c] = 0

                # Dano no Player
                if player.rect.colliderect(explosao_rect):
                    player.receber_dano()

                # Dano nos Inimigos
                for inimigo in inimigos:
                    if inimigo.rect.colliderect(explosao_rect):
                        inimigo.receber_dano_explosao()


# CLASSE MÃE 
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



# CLASSE FILHA
class Fantasma(Inimigo):
    COR_NORMAL = (255, 225, 255)   # Branco-rosado
    COR_FURIA  = (100, 100, 255)   # Azul intenso

    def __init__(self, x, y):
        # Chama o __init__ da classe mãe com os atributos do Fantasma
        super().__init__(
            x=x, y=y,
            largura=45, altura=45,
            velocidade=2,
            vida=3,
            cor=Fantasma.COR_NORMAL
        )
        self.furia_timer = 0
        self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
        self.contador_passos = 0

    # Sobrescrita do método da classe mãe
    def receber_dano_explosao(self):
        """
        Comportamento ESPECIAL do Fantasma:
        além de perder vida, entra em modo fúria.
        """
        super().receber_dano_explosao() 
        if self.ativo:                  
            self._ativar_furia()

    def _ativar_furia(self):
        if self.furia_timer <= 0:
            self.furia_timer = 180  # 3 segundos de fúria
            print(f"[FANTASMA] Entrou em fúria! Vida restante: {self.vida}")

    def _colidiu_com_parede_solida(self, mapa):
        """
        Retorna True se o rect atual do fantasma sobrepõe algum tile de
        parede INQUEBRÁVEL (tile == 1) no mapa.
        Minérios (tile == 2) são ignorados no modo fúria o fantasma os atravessa.
        """
        # Verifica os quatro cantos do rect do fantasma
        pontos = [
            (self.rect.left  + 2, self.rect.top    + 2),
            (self.rect.right - 2, self.rect.top    + 2),
            (self.rect.left  + 2, self.rect.bottom - 2),
            (self.rect.right - 2, self.rect.bottom - 2),
        ]
        for px, py in pontos:
            col = px // 50
            lin = py // 50
            if 0 <= lin < len(mapa) and 0 <= col < len(mapa[0]):
                if mapa[lin][col] == 1:   # somente parede inquebrável bloqueia
                    return True
        return False

    #Sobrescrita do método abstrato da classe mãe
    def mover(self, player, paredes, mapa=None):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y

        # MODO FÚRIA: persegue o player, atravessa minérios, MAS respeita paredes sólidas
        if self.furia_timer > 0:
            self.furia_timer -= 1
            self.cor = Fantasma.COR_FURIA

            # Move em X e verifica apenas paredes sólidas (tile 1)
            if self.rect.x < player.rect.x: self.rect.x += self.velocidade
            elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade
            if mapa and self._colidiu_com_parede_solida(mapa):
                self.rect.x = pos_antiga_x  # Reverte só X

            # Atualiza pos_antiga_y após resolver X
            pos_antiga_y = self.rect.y

            # Move em Y e verifica apenas paredes sólidas (tile 1)
            if self.rect.y < player.rect.y: self.rect.y += self.velocidade
            elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade
            if mapa and self._colidiu_com_parede_solida(mapa):
                self.rect.y = pos_antiga_y  # Reverte só Y

        # MODO NORMAL: movimento aleatório, respeita todas as paredes
        else:
            self.cor = Fantasma.COR_NORMAL

            if self.direcao == 'cima':       self.rect.y -= self.velocidade
            elif self.direcao == 'baixo':    self.rect.y += self.velocidade
            elif self.direcao == 'esquerda': self.rect.x -= self.velocidade
            elif self.direcao == 'direita':  self.rect.x += self.velocidade

            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x = pos_antiga_x
                    self.rect.y = pos_antiga_y
                    self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                    break

            self.contador_passos += 1
            if self.contador_passos > 60:
                self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                self.contador_passos = 0



# CLASSE FILHA — GOLEM  (herda de Inimigo)
class Golem(Inimigo):
    COR_NORMAL  = (139, 90, 43)    # Marrom pedra
    COR_ALERTA  = (200, 60, 20)    # Laranja-avermelhado ao perseguir

    def __init__(self, x, y):
        # Chama o __init__ da classe mãe com os atributos do Golem
        super().__init__(
            x=x, y=y,
            largura=45, altura=45,
            velocidade=1,           # Mais lento que o Fantasma
            vida=5,                 # Mais resistente que o Fantasma
            cor=Golem.COR_NORMAL
        )
        self.raio_deteccao = 250    # Distância (px) para o Golem notar o player
        self.cooldown_knockback = 0 # Impede knockback consecutivo

    def _distancia_para(self, player):
        """Calcula a distância entre o Golem e o Player."""
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return (dx**2 + dy**2) ** 0.5

    #Sobrescrita do método abstrato da classe mãe
    def mover(self, player, paredes, mapa=None):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
        distancia = self._distancia_para(player)

        # Só age se o player estiver dentro do raio de detecção
        if distancia <= self.raio_deteccao:
            self.cor = Golem.COR_ALERTA

            # Persegue o player em X
            if self.rect.x < player.rect.x: self.rect.x += self.velocidade
            elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade

            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x = pos_antiga_x
                    break

            # Persegue o player em Y
            if self.rect.y < player.rect.y: self.rect.y += self.velocidade
            elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade

            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.y = pos_antiga_y
                    break
        else:
            self.cor = Golem.COR_NORMAL  # Fica parado fora do raio

        # Atualiza cooldown do knockback
        if self.cooldown_knockback > 0:
            self.cooldown_knockback -= 1

    def aplicar_knockback_no_player(self, player):
        """
        ao colidir com o player, empurra ele para longe além de causar dano.
        """
        if self.rect.colliderect(player.rect):
            player.receber_dano()
            if self.cooldown_knockback == 0:
                player.aplicar_knockback(self.rect)
                self.cooldown_knockback = 90  # Evita knockback spam (1,5s)
                print("[GOLEM] Knockback aplicado no Mike!")
