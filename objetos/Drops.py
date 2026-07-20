import random
from objetos.Item import Item
from config import TELA_SIZE
 
# drops por classe de mob: (item, chance)
# chance vai de 0.0 a 1.0
DROPS_MOBS = {
    "Fantasma":          [("Plasma", 0.80), ("Essencia Fantasmal", 0.20)],
    "LegiaoDeFantasmas": [("Plasma", 0.80), ("Essencia Fantasmal", 0.25)],
    "CogumeloEsporos":   [("Esporos", 0.85), ("Nucleo de Esporos", 0.15)],
    "CogumeloAgressivo": [("Esporos", 0.70), ("Chapeu de Cogumelo", 0.60)],
    "Goblin":            [("Madeira", 0.85), ("Olho de Goblin", 0.20)],
    "Slime":             [("Gosma", 0.80), ("Musgo", 0.60)],
    "Golem":             [("Musgo", 0.70), ("Minerio Comum", 0.80), ("Minerio Raro", 0.15)],
    "GolemLava":         [("Musgo", 0.70), ("Minerio Comum", 0.80), ("Minerio Raro", 0.15)],  # pedido: mesmo drop do golem comum
}
 
# drops de tiles destruídos pela bomba
DROPS_TILES = {
    2: [("Minerio Comum", 0.40)],                          # pedra
    4: [("Minerio Comum", 0.70), ("Cristais", 0.25), ("Minerio Raro", 0.10)],  # minério
}
 
def gerar_drops_mob(inimigo):
    """Retorna lista de Items gerados ao matar um mob."""
    nome  = inimigo.__class__.__name__
    tabela = DROPS_MOBS.get(nome, [])
    itens  = []
    for tipo, chance in tabela:
        if random.random() < chance:
            itens.append(Item(inimigo.rect.centerx, inimigo.rect.centery, tipo))
    return itens
 
def gerar_drops_tile(col, lin, tile_tipo):
    """Retorna lista de Items gerados ao destruir um tile."""
    tabela = DROPS_TILES.get(tile_tipo, [])
    itens  = []
    x = col * TELA_SIZE + TELA_SIZE // 2
    y = lin * TELA_SIZE + TELA_SIZE // 2
    for tipo, chance in tabela:
        if random.random() < chance:
            itens.append(Item(x, y, tipo))
    return itens
