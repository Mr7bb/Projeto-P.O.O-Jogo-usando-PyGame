import pygame
import math
from entidades.Golem import Golem
 
class GolemLava(Golem):
    """
    golem de lava: uma versao mais forte do golem comum, mora no mesmo bioma dele (bioma 4).
    herda o mover() (patrulha/perseguicao) do Golem sem mudar nada, entao ele anda igualzinho.
    a diferenca e o ataque novo: de vez em quando ele bate no chao e acerta o player a
    distancia, deixando ele pegando fogo por uns segundos (dano ao longo do tempo).
    nao e mais o boss do jogo (o boss vai ser refeito), agora e so um mob comum e mais forte.
    """
 
    COR_NORMAL_LAVA = (60, 30, 20)     
    COR_ALERTA_LAVA = (255, 90, 20)    
    COR_AVISO       = (255, 210, 70)   
 
    ALCANCE_ATAQUE = 190     # distancia maxima pra ele conseguir bater o solo e acertar o player
    TEMPO_AVISO    = 45      # frames "carregando" o golpe antes de bater (da tempo do player fugir)
    COOLDOWN_BASE  = 210     # cooldown entre um golpe de solo e o proximo
    DURACAO_FOGO   = 180     # 3 segundos de queimadura (60 fps)
    DANO_IMPACTO   = 25
 
    def __init__(self, x, y):
        super().__init__(x, y)
        # mais vida e mais lento que o golem comum: ele compensa a lentidao com o ataque a distancia
        self.vida = 9
        self.velocidade = 0.8
        self.cor = self.COR_NORMAL_LAVA
        # sobrescreve as cores herdadas do Golem comum pra ficar com a paleta de lava
        self.COR_NORMAL = self.COR_NORMAL_LAVA
        self.COR_ALERTA = self.COR_ALERTA_LAVA
 
        self.cooldown_ataque_solo = 90   # comeca com cooldown, pra nao bater assim que a fase carrega
        self.avisando_ataque = False
        self.timer_aviso = 0
        self.crosta_timer = 0            # controla por quantos frames o efeito visual da crosta fica na tela
 
    def atacar_solo(self, player):
        """
        chamado todo frame la no Blast_Miner.py. controla o ciclo do golpe de solo:
        1) espera o cooldown acabar e o player entrar no alcance
        2) fica "avisando" por TEMPO_AVISO frames (pisca), pra dar chance do player fugir
        3) quando o aviso acaba, se o player ainda estiver perto, aplica dano + fogo
        """
        if self.cooldown_ataque_solo > 0:
            self.cooldown_ataque_solo -= 1
 
        dist = self._distancia_para(player)
 
        if not self.avisando_ataque:
            if self.cooldown_ataque_solo <= 0 and dist <= self.ALCANCE_ATAQUE:
                self.avisando_ataque = True
                self.timer_aviso = self.TEMPO_AVISO
        else:
            self.timer_aviso -= 1
            # pisca entre vermelho forte e amarelo pra avisar que o golpe ta chegando
            self.cor = self.COR_ALERTA_LAVA if (self.timer_aviso // 5) % 2 == 0 else self.COR_AVISO
 
            if self.timer_aviso <= 0:
                self.avisando_ataque = False
                self.cooldown_ataque_solo = self.COOLDOWN_BASE
                self.crosta_timer = 40   # liga o efeito visual da crosta de lava por um tempinho
                self.cor = self.COR_NORMAL_LAVA
 
                # so acerta o player se ele continuar no alcance quando o golpe realmente cai
                if self._distancia_para(player) <= self.ALCANCE_ATAQUE:
                    player.receber_dano(self.DANO_IMPACTO)
                    player._fogo_timer = self.DURACAO_FOGO
 
    def desenhar(self, tela):
        # crosta de lava/pedras no chao ao redor dele, some sozinha depois de um tempo
        if self.crosta_timer > 0:
            self.crosta_timer -= 1
            cx, cy = self.rect.centerx, self.rect.centery
            for i in range(6):
                ang = (i / 6) * 2 * math.pi
                px = int(cx + 40 * math.cos(ang))
                py = int(cy + 40 * math.sin(ang))
                pygame.draw.circle(tela, (90, 30, 10), (px, py), 8)
                pygame.draw.circle(tela, (255, 120, 30), (px, py), 4)
 
        # anel se expandindo avisando onde o golpe vai cair (telegraph)
        if self.avisando_ataque:
            raio_aviso = max(1, int(self.ALCANCE_ATAQUE * (1 - self.timer_aviso / self.TEMPO_AVISO)))
            pygame.draw.circle(tela, (255, 90, 20), self.rect.center, raio_aviso, 2)
 
        super().desenhar(tela)
