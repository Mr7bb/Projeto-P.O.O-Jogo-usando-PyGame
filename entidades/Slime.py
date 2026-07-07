
import pygame
import random
from entidades.Inimigo import Inimigo
 
class Slime(Inimigo):
    COR  = (60, 200, 120)
    COR_MINI = (40, 160, 90)
 
    def __init__(self, x, y, mini=False):
        tamanho = 28 if mini else 42
        super().__init__(x, y, largura=tamanho, altura=tamanho,
                         velocidade=1, vida=2 if not mini else 1,
                         cor=self.COR_MINI if mini else self.COR)
        self.mini = mini
        self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
        self.contador_passos = 0
        self.dividiu = False  # flag pra evitar divisão em loop
 
    def receber_dano_explosao(self):
        # bomba mata instantaneamente qualquer slime
        self.vida = 0
        self.ativo = False
        print("[SLIME] Destruído pela explosão!")
 
    def receber_dano_espada(self):
        # espada divide (apenas slimes grandes)
        if not self.mini and not self.dividiu:
            self.dividiu = True
            self.ativo = False
            print("[SLIME] Dividido!")
            return True  # sinaliza pra Blast_Miner spawnar 2 mini slimes
        else:
            self.vida -= 1
            if self.vida <= 0:
                self.ativo = False
            return False
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        pos_antiga_x = self.rect.x
        pos_antiga_y = self.rect.y
 
        if self.direcao == 'cima':    self.rect.y -= self.velocidade
        elif self.direcao == 'baixo': self.rect.y += self.velocidade
        elif self.direcao == 'esquerda': self.rect.x -= self.velocidade
        elif self.direcao == 'direita':  self.rect.x += self.velocidade
 
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x = pos_antiga_x
                self.rect.y = pos_antiga_y
                self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
                break
 
        self.contador_passos += 1
        if self.contador_passos > 80:
            self.direcao = random.choice(['cima', 'baixo', 'esquerda', 'direita'])
            self.contador_passos = 0
 
    def desenhar(self, tela):
        # corpo arredondado
        pygame.draw.ellipse(tela, self.cor, self.rect)
        # olhinhos
        ox = self.rect.centerx
        oy = self.rect.centery - 4
        pygame.draw.circle(tela, (20, 20, 20), (ox - 6, oy), 3)
        pygame.draw.circle(tela, (20, 20, 20), (ox + 6, oy), 3)