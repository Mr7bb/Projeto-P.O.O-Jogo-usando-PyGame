import pygame
from objetos.Item import ITENS

# ── definição dos upgrades ──────────────────────────────────────────────

# cada upgrade: (nome_display, atributo_player, custo_dict, max_nivel)
UPGRADES_FERREIRO = [
    {
        "nome":   "Forca da Espada",
        "attr":   "nivel_forca",
        "custo":  {"Minerio Comum": 2, "Cristais": 1},
        "max":    5,
        "icone":  "⚔",
        "desc":   "Aumenta o dano da espada",
    },
    {
        "nome":   "Alcance da Bomba",
        "attr":   "nivel_bomba_alcance",
        "custo":  {"Minerio Comum": 2, "Madeira": 2},
        "max":    3,
        "icone":  "💣",
        "desc":   "Aumenta o raio da explosão",
    },
    {
        "nome":   "Pavio mais Rapido",
        "attr":   "nivel_bomba_cd",
        "custo":  {"Madeira": 3, "Minerio Raro": 1},
        "max":    3,
        "icone":  "⏱",
        "desc":   "Reduz o cooldown da bomba",
    },
    {
        "nome":   "Segunda Bomba",
        "attr":   "nivel_bombas_simult",
        "custo":  {"Minerio Raro": 2, "Cristais": 2},
        "max":    1,
        "icone":  "💥",
        "desc":   "Permite plantar 2 bombas ao mesmo tempo",
    },
]

UPGRADES_AMBULANTE = [
    {
        "nome":   "Vida Extra",
        "attr":   "nivel_hp",
        "custo":  {"Essencia Fantasmal": 1, "Gosma": 2},
        "max":    5,
        "icone":  "❤",
        "desc":   "Aumenta o HP máximo em +25",
    },
    {
        "nome":   "Velocidade",
        "attr":   "nivel_velocidade",
        "custo":  {"Esporos": 2, "Musgo": 2},
        "max":    4,
        "icone":  "💨",
        "desc":   "Aumenta a velocidade de movimento",
    },
    {
        "nome":   "Imunidade a Veneno",
        "attr":   "imune_veneno",
        "custo":  {"Nucleo de Esporos": 1, "Chapeu de Cogumelo": 1},
        "max":    1,
        "icone":  "🛡",
        "desc":   "Você nunca mais será envenenado",
    },
    {
        "nome":   "Escudo Temporario",
        "attr":   "nivel_escudo",
        "custo":  {"Gosma": 2, "Musgo": 1, "Olho de Goblin": 1},
        "max":    3,
        "icone":  "🔮",
        "desc":   "Ganha 1 carga de escudo por fase",
    },
]


class TelaLoja:
    COR_FUNDO   = (15, 15, 30, 210)
    COR_TITULO  = (255, 200, 50)
    COR_OK      = (80, 220, 80)
    COR_CARO    = (200, 80, 80)
    COR_MAX     = (120, 120, 120)
    COR_SEL     = (60, 80, 160)
    COR_HOVER   = (40, 55, 120)

    def __init__(self, tela):
        self.tela    = tela
        self.W, self.H = tela.get_size()
        self.visivel = False
        self.tipo    = None      # 'ferreiro' ou 'ambulante'
        self.sel     = 0         # índice selecionado
        self._fonte_titulo = pygame.font.SysFont("monospace", 26, bold=True)
        self._fonte_item   = pygame.font.SysFont("monospace", 18, bold=True)
        self._fonte_desc   = pygame.font.SysFont("monospace", 14)
        self._fonte_custo  = pygame.font.SysFont("monospace", 14)

    def abrir(self, tipo):
        self.visivel = True
        self.tipo    = tipo
        self.sel     = 0

    def fechar(self):
        self.visivel = False
        self.tipo    = None

    def _upgrades(self):
        return UPGRADES_FERREIRO if self.tipo == "ferreiro" else UPGRADES_AMBULANTE

    def _pode_comprar(self, upgrade, inventario, player):
        if self._nivel_atual(upgrade, player) >= upgrade["max"]:
            return False, "MAX"
        for item, qtd in upgrade["custo"].items():
            if not inventario.tem(item, qtd):
                return False, "SEM RECURSOS"
        return True, "COMPRAR"

    def _nivel_atual(self, upgrade, player):
        attr = upgrade["attr"]
        return getattr(player, attr, 0)

    def handle_event(self, event, inventario, player):
        if not self.visivel:
            return
        upgrades = self._upgrades()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_e):
                self.fechar()
            elif event.key == pygame.K_UP:
                self.sel = (self.sel - 1) % len(upgrades)
            elif event.key == pygame.K_DOWN:
                self.sel = (self.sel + 1) % len(upgrades)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._comprar(upgrades[self.sel], inventario, player)

    def _comprar(self, upgrade, inventario, player):
        pode, _ = self._pode_comprar(upgrade, inventario, player)
        if not pode:
            return

        # debita do inventário
        for item, qtd in upgrade["custo"].items():
            inventario.remover(item, qtd)

        attr = upgrade["attr"]

        # aplica efeito no player
        if attr == "nivel_hp":
            player.nivel_hp += 1
            player.aumentar_hp_max(25)
        elif attr == "nivel_velocidade":
            player.nivel_velocidade += 1
            player.velocidade += 1
        elif attr == "nivel_forca":
            player.nivel_forca += 1
            # dano base sobe: 10 + nivel*4
            for k in player.DANO_ESPADA:
                player.DANO_ESPADA[k] = max(player.DANO_ESPADA[k],
                                             10 + player.nivel_forca * 4)
            player.DANO_ESPADA_PADRAO = 10 + player.nivel_forca * 4
        elif attr == "nivel_bomba_alcance":
            player.nivel_bomba_alcance += 1
        elif attr == "nivel_bomba_cd":
            player.nivel_bomba_cd += 1
            player.BOMBA_COOLDOWN_BASE = max(60, player.BOMBA_COOLDOWN_BASE - 30)
        elif attr == "nivel_bombas_simult":
            player.nivel_bombas_simult = 1
            player.max_bombas = 2
        elif attr == "imune_veneno":
            player.imune_veneno = True
        elif attr == "nivel_escudo":
            player.nivel_escudo += 1
            player.escudo_cargas += 1

        print(f"[LOJA] Comprou: {upgrade['nome']}")

    def draw(self, inventario, player):
        if not self.visivel:
            return

        upgrades = self._upgrades()
        nome_loja = "Ferreiro" if self.tipo == "ferreiro" else "Ambulante Mistico"

        # overlay semitransparente
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill(self.COR_FUNDO)
        self.tela.blit(overlay, (0, 0))

        # painel central
        pw, ph = 700, 500
        px = (self.W - pw) // 2
        py = (self.H - ph) // 2
        pygame.draw.rect(self.tela, (20, 20, 45), (px, py, pw, ph), border_radius=10)
        pygame.draw.rect(self.tela, (80, 80, 160), (px, py, pw, ph), 2, border_radius=10)

        # título
        titulo = self._fonte_titulo.render(f"[ {nome_loja} ]", True, self.COR_TITULO)
        self.tela.blit(titulo, (px + pw // 2 - titulo.get_width() // 2, py + 16))

        # instrução
        inst = self._fonte_desc.render("↑↓ navegar   ENTER comprar   E/ESC fechar", True, (140, 140, 180))
        self.tela.blit(inst, (px + pw // 2 - inst.get_width() // 2, py + 48))

        # lista de upgrades
        for i, upg in enumerate(upgrades):
            iy = py + 90 + i * 88
            selecionado = i == self.sel
            pode, status = self._pode_comprar(upg, inventario, player)
            nivel = self._nivel_atual(upg, player)

            # fundo do item
            fundo_cor = self.COR_SEL if selecionado else (30, 30, 60)
            pygame.draw.rect(self.tela, fundo_cor, (px + 10, iy, pw - 20, 78), border_radius=6)
            if selecionado:
                pygame.draw.rect(self.tela, (100, 120, 220), (px + 10, iy, pw - 20, 78), 2, border_radius=6)

            # ícone + nome
            nome_txt = self._fonte_item.render(f"{upg['icone']}  {upg['nome']}", True, (220, 220, 255))
            self.tela.blit(nome_txt, (px + 22, iy + 8))

            # nível atual
            nivel_str = f"Nível: {'■' * nivel}{'□' * (upg['max'] - nivel)}  ({nivel}/{upg['max']})"
            nivel_txt = self._fonte_desc.render(nivel_str, True, (160, 200, 160))
            self.tela.blit(nivel_txt, (px + 22, iy + 32))

            # descrição
            desc_txt = self._fonte_desc.render(upg["desc"], True, (160, 160, 200))
            self.tela.blit(desc_txt, (px + 22, iy + 50))

            # custo
            custo_parts = []
            for item, qtd in upg["custo"].items():
                tem = inventario.itens.get(item, 0)
                custo_parts.append(f"{item}:{tem}/{qtd}")
            custo_str = "  ".join(custo_parts)
            cor_custo = self.COR_OK if pode else (self.COR_MAX if nivel >= upg["max"] else self.COR_CARO)
            custo_txt = self._fonte_custo.render(custo_str, True, cor_custo)
            self.tela.blit(custo_txt, (px + pw - custo_txt.get_width() - 20, iy + 10))

            # status
            status_txt = self._fonte_custo.render(f"[ {status} ]", True, cor_custo)
            self.tela.blit(status_txt, (px + pw - status_txt.get_width() - 20, iy + 32))