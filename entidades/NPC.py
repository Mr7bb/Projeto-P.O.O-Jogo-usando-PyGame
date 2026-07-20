import pygame
 
class NPC:
    """ferreiro ou ambulante mistico. so aparecem no mapa e ficam parados esperando o player chegar perto."""
 
    RAIO_INTERACAO = 80  # distância pra mostrar prompt de E
 
    # BUG DE FPS CORRIGIDO: antes desenhar() criava 2 fontes NOVAS (pygame.font.SysFont)
    # toda vez que era chamado, ou seja, todo frame, pra cada npc na tela. SysFont e uma
    # chamada cara (o pygame vai la no sistema operacional procurar a fonte de novo cada
    # vez), entao isso sozinho ja derrubava o fps quando os npcs apareciam. agora as fontes
    # sao criadas so uma vez (atributo de classe, compartilhado por todos os npcs) e
    # reaproveitadas em todo desenhar().
    _fonte_label = None
    _fonte_nome  = None
 
    def __init__(self, x, y, tipo):
        """tipo: 'ferreiro' ou 'ambulante'"""
        self.tipo  = tipo
        self.rect  = pygame.Rect(x, y, 40, 40)
        self.ativo = True
 
        if tipo == "ferreiro":
            self.cor    = (180, 140, 60)
            self.nome   = "Ferreiro"
            self.label  = "F"
        else:
            self.cor    = (120, 80, 200)
            self.nome   = "Ambulante Mistico"
            self.label  = "A"
 
        if NPC._fonte_label is None:
            NPC._fonte_label = pygame.font.SysFont("monospace", 18, bold=True)
            NPC._fonte_nome  = pygame.font.SysFont("monospace", 13)
 
    def perto_do_player(self, player):
        dist = ((self.rect.centerx - player.rect.centerx)**2 +
                (self.rect.centery - player.rect.centery)**2) ** 0.5
        return dist <= self.RAIO_INTERACAO
 
    def desenhar(self, tela, cam_x=0, cam_y=0):
        rx = self.rect.x - cam_x
        ry = self.rect.y - cam_y
 
        # corpo
        pygame.draw.rect(tela, self.cor, (rx, ry, self.rect.width, self.rect.height), border_radius=6)
        # borda brilhante
        brilho = tuple(min(v + 60, 255) for v in self.cor)
        pygame.draw.rect(tela, brilho, (rx, ry, self.rect.width, self.rect.height), 2, border_radius=6)
 
        # letra identificadora (fonte cacheada, ver comentario la em cima da classe)
        txt = NPC._fonte_label.render(self.label, True, (255, 255, 255))
        tela.blit(txt, (rx + self.rect.width  // 2 - txt.get_width()  // 2,
                        ry + self.rect.height // 2 - txt.get_height() // 2))
 
        # nome acima
        nome_txt = NPC._fonte_nome.render(self.nome, True, (220, 220, 220))
        tela.blit(nome_txt, (rx + self.rect.width // 2 - nome_txt.get_width() // 2, ry - 18))
    