import pygame
import random
from entidades.Inimigo import Inimigo
 
class Slime(Inimigo):
    """
    slime que anda patrulhando sozinho. quando o slime grande (mini=False) toma uma espadada,
    ele nao morre: ele "divide" em 2 slimes mini (isso e controlado la no Blast_Miner.py,
    aqui a gente so avisa que dividiu retornando True).
    """
 
    COR  = (60, 200, 120)
    COR_MINI = (40, 160, 90)
 
    def __init__(self, x, y, mini=False):
        tamanho = 28 if mini else 42
        # mini: vida 1 -> 3 (agora precisa de 2 picaretadas em vez de morrer numa so)
        vida_inicial = 3 if mini else 2
        super().__init__(x, y, largura=tamanho, altura=tamanho, velocidade=1, vida=vida_inicial, cor=self.COR_MINI if mini else self.COR)
        self.mini = mini
        self.dividiu = False  
        # direcao_patrulha/passos_patrulha ja vem prontos da classe mae (Inimigo.__init__)
 
    def receber_dano_explosao(self):
        # bomba sempre destroi o slime na hora, nao importa o tamanho
        self.vida = 0
        self.ativo = False
        print("[SLIME] Destruído pela explosão!")
 
    def receber_dano_picareta(self, dano, player_rect):
        # slime grande: a primeira picaretada nao mata, ela faz ele dividir em 2 minis
        # (quem realmente cria os 2 minis novos e o Blast_Miner.py, que le esse retorno True)
        if not self.mini and not self.dividiu:
            self.dividiu = True
            self.ativo = False
            print("[SLIME] Dividido!")
            return True  
        else:
            super().receber_dano_picareta(dano, player_rect)
            return False
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        # slime nao persegue ninguem, so fica patrulhando o tempo todo (metodo da classe mae)
        self._patrulhar_aleatorio(paredes, passos_max=80)
 
    def desenhar(self, tela):
        pygame.draw.ellipse(tela, self.cor, self.rect)
        ox, oy = self.rect.centerx, self.rect.centery - 4
        pygame.draw.circle(tela, (20, 20, 20), (ox - 6, oy), 3)
        pygame.draw.circle(tela, (20, 20, 20), (ox + 6, oy), 3)
