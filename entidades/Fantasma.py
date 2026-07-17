import pygame
import random
from entidades.Inimigo import Inimigo

class Fantasma(Inimigo):
    COR_NORMAL = (255, 225, 255)   # Branco-rosado
    COR_FURIA  = (100, 100, 255)   # Azul intenso

    def __init__(self, x, y):
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

    def receber_dano_explosao(self):
        super().receber_dano_explosao() 
        if self.ativo:                  
            self._ativar_furia()

    def _ativar_furia(self):
        if self.furia_timer <= 0:
            self.furia_timer = 180  # 3 segundos de fúria
            print(f"[FANTASMA] Entrou em fúria! Vida restante: {self.vida}")

    def _colidiu_com_parede_solida(self, mapa):
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
                # Fantasmas voam por cima da água (5) e de minérios, colidindo apenas com Parede Inquebrável (1)
                if mapa[lin][col] == 1:   
                    return True
        return False

    def mover(self, player, paredes, mapa=None, bombas=None):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y

        # MODO FÚRIA: persegue o player, atravessa minérios/águas, respeita paredes sólidas
        if self.furia_timer > 0:
            self.furia_timer -= 1
            self.cor = Fantasma.COR_FURIA

            # Move em X
            if self.rect.x < player.rect.x: self.rect.x += self.velocidade
            elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade
            if mapa and self._colidiu_com_parede_solida(mapa):
                self.rect.x = pos_antiga_x  
            if bombas:
                for b in bombas:
                    if b.solida and self.rect.colliderect(b.rect):
                        self.rect.x = pos_antiga_x
            
            pos_antiga_y = self.rect.y

            # Move em Y
            if self.rect.y < player.rect.y: self.rect.y += self.velocidade
            elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade
            if mapa and self._colidiu_com_parede_solida(mapa):
                self.rect.y = pos_antiga_y  
            if bombas:
                for b in bombas:
                    if b.solida and self.rect.colliderect(b.rect):
                        self.rect.y = pos_antiga_y

        # MODO NORMAL: movimento aleatório, respeita todas as colisões passadas pela lista de paredes
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
                        self.rect.x = pos_antiga_x
                        self.rect.y = pos_antiga_y
                        self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                        break

            self.contador_passos += 1
            if self.contador_passos > 60:
                self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                self.contador_passos = 0


class LegiaoDeFantasmas(Fantasma):
    COR_LEGIAO = (180, 100, 255)

    def __init__(self, x, y, grupo):
        super().__init__(x, y)
        self.vida = 4
        self.cor = self.COR_LEGIAO
        self.grupo = grupo  

    def receber_dano_explosao(self):
        super().receber_dano_explosao()
        for membro in self.grupo:
            if membro.ativo and membro is not self:
                membro._ativar_furia()
        print(f"[LEGIÃO] Membro atingido — toda a legião em fúria!")