import pygame
import random
import math  # estava sendo importado dentro do desenhar() toda vez, movi pra ca (so precisa 1 vez)

# cores e símbolos por tipo de item
ITENS = {
    # orgânicos
    "Plasma":             {"cor": (180, 100, 255), "simbolo": "P"},
    "Essencia Fantasmal": {"cor": (220, 180, 255), "simbolo": "E"},
    "Esporos":            {"cor": (120, 200,  60), "simbolo": "S"},
    "Nucleo de Esporos":  {"cor": ( 60, 160,  30), "simbolo": "N"},
    "Chapeu de Cogumelo": {"cor": (200,  80,  80), "simbolo": "C"},
    "Gosma":              {"cor": ( 80, 220, 120), "simbolo": "G"},
    "Musgo":              {"cor": ( 60, 140,  60), "simbolo": "M"},
    "Olho de Goblin":     {"cor": (255, 200,   0), "simbolo": "O"},
    # minerais
    "Minerio Comum":      {"cor": (180, 140,  80), "simbolo": "m"},
    "Minerio Raro":       {"cor": (100, 200, 255), "simbolo": "R"},
    "Cristais":           {"cor": (120, 220, 255), "simbolo": "K"},
    "Madeira":            {"cor": (160, 110,  60), "simbolo": "W"},
}

ORGANICOS = {"Plasma", "Essencia Fantasmal", "Esporos", "Nucleo de Esporos",
             "Chapeu de Cogumelo", "Gosma", "Musgo", "Olho de Goblin"}
MINERAIS  = {"Minerio Comum", "Minerio Raro", "Cristais", "Madeira"}

class Item:
    TAMANHO = 20

    # mesma correcao de fps do NPC.py: antes cada item no chao criava uma fonte NOVA
    # toda vez que desenhava (todo frame, pra cada item, e podem ter varios itens
    # no chao ao mesmo tempo). agora e uma fonte so, compartilhada por todos os itens,
    # criada apenas na primeira vez que algum item precisa desenhar.
    _fonte = None

    def __init__(self, x, y, tipo):
        self.tipo  = tipo
        self.ativo = True
        # posição com pequeno offset aleatório pra não empilhar tudo
        ox = random.randint(-15, 15)
        oy = random.randint(-15, 15)
        self.rect = pygame.Rect(x + ox, y + oy, self.TAMANHO, self.TAMANHO)
        self._bob_timer = random.randint(0, 60)  # animação de bobbing

    def atualizar(self, player):
        # coleta automática ao tocar no player
        if self.rect.colliderect(player.rect):
            self.ativo = False
            return self.tipo
        # bobbing vertical simples
        self._bob_timer += 1
        return None

    def desenhar(self, tela, cam_x=0, cam_y=0):
        bob = int(math.sin(self._bob_timer * 0.08) * 3)
        rx  = self.rect.x - cam_x
        ry  = self.rect.y - cam_y + bob

        info = ITENS.get(self.tipo, {"cor": (200, 200, 200), "simbolo": "?"})
        cor  = info["cor"]

        # fundo circular
        cx = rx + self.TAMANHO // 2
        cy = ry + self.TAMANHO // 2
        pygame.draw.circle(tela, cor, (cx, cy), self.TAMANHO // 2)
        brilho = tuple(min(v + 60, 255) for v in cor)
        pygame.draw.circle(tela, brilho, (cx - 2, cy - 2), self.TAMANHO // 4)

        # letra identificadora (fonte cacheada, ver comentario la em cima da classe)
        if Item._fonte is None:
            Item._fonte = pygame.font.SysFont("monospace", 11, bold=True)
        txt = Item._fonte.render(info["simbolo"], True, (20, 20, 20))
        tela.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))
