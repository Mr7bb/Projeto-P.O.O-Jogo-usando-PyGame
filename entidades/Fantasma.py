import pygame
import random
from entidades.Inimigo import Inimigo
from objetos.Bomba import Bomba
 
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
    def mover(self, player, paredes, mapa=None, bombas=None):
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
            if bombas:
                for  b in  bombas:
                    if b.solida and self.rect.colliderect(b.rect):
                        self.rect.x = pos_antiga_x
            # Atualiza pos_antiga_y após resolver X
            pos_antiga_y = self.rect.y
 
            # Move em Y e verifica apenas paredes sólidas (tile 1)
            if self.rect.y < player.rect.y: self.rect.y += self.velocidade
            elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade
            if mapa and self._colidiu_com_parede_solida(mapa):
                self.rect.y = pos_antiga_y  # Reverte só Y
            if bombas:
                for  b in  bombas:
                    if b.solida and self.rect.colliderect(b.rect):
                        self.rect.x = pos_antiga_y
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
            if bombas:
                for b in bombas:
                    if b.solida and self.rect.colliderect(b.rect):
                        self.rect.x =  pos_antiga_x
                        self.rect.y =  pos_antiga_y
                        self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                        break
 
            self.contador_passos += 1
            if self.contador_passos > 60:
                self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                self.contador_passos = 0
 
 
class LegiaoDeFantasmas(Fantasma):
    """Como o Fantasma Padrão, mas quando um é atingido todos entram em fúria."""
    COR_LEGIAO = (180, 100, 255)
 
    def __init__(self, x, y, grupo=None):
        super().__init__(x, y)
        self.vida = 4
        self.cor = self.COR_LEGIAO
        self.grupo = grupo or []  # lista com todos os membros da legião
 
    def receber_dano_explosao(self):
        super().receber_dano_explosao()
        # ativa fúria em todos do grupo
        for membro in self.grupo:
            if membro.ativo and membro is not self:
                membro._ativar_furia()
        print(f"[LEGIÃO] Membro atingido — toda a legião em fúria!")