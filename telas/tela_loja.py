import pygame
from objetos.Item import ITENS

UPGRADES_FERREIRO = [
    {"nome": "Forca da Picareta", "attr": "nivel_forca", "custo": {"Minerio Comum": 2, "Cristais": 1}, "max": 5, "icone": "⚔", "desc": "Aumenta o dano da picareta"},
    {"nome": "Alcance da Bomba", "attr": "nivel_bomba_alcance", "custo": {"Minerio Comum": 2, "Madeira": 2}, "max": 3, "icone": "💣", "desc": "Aumenta o raio da explosão"},
    {"nome": "Pavio mais Rapido", "attr": "nivel_bomba_cd", "custo": {"Madeira": 3, "Minerio Raro": 1}, "max": 3, "icone": "⏱", "desc": "Reduz o cooldown da bomba"},
    {"nome": "Segunda Bomba", "attr": "nivel_bombas_simult", "custo": {"Minerio Raro": 2, "Cristais": 2}, "max": 1, "icone": "💥", "desc": "Permite plantar 2 bombas ao mesmo tempo"},
]

UPGRADES_AMBULANTE = [
    {"nome": "Vida Extra", "attr": "nivel_hp", "custo": {"Essencia Fantasmal": 1, "Gosma": 2}, "max": 5, "icone": "❤", "desc": "Aumenta o HP máximo em +25"},
    {"nome": "Velocidade", "attr": "nivel_velocidade", "custo": {"Esporos": 2, "Musgo": 2}, "max": 4, "icone": "💨", "desc": "Aumenta a velocidade de movimento"},
    {"nome": "Imunidade a Veneno", "attr": "imune_veneno", "custo": {"Nucleo de Esporos": 1, "Chapeu de Cogumelo": 1}, "max": 1, "icone": "🛡", "desc": "Você nunca mais será envenenado"},
    {"nome": "Escudo Temporario", "attr": "nivel_escudo", "custo": {"Gosma": 2, "Musgo": 1, "Olho de Goblin": 1}, "max": 3, "icone": "🔮", "desc": "Ganha 1 carga de escudo por fase"},
    # pedido: um item pra recuperar hp na hora (nao so aumentar o maximo). e "consumivel":
    # pode comprar varias vezes, nao tem "nivel" que vai subindo pra sempre igual os outros
    {"nome": "Pocao de Cura", "attr": "curar_hp", "custo": {"Gosma": 1, "Esporos": 1}, "max": 1, "icone": "💚", "desc": "Recupera 60 de HP na hora", "consumivel": True},
]

class TelaLoja:
    COR_FUNDO   = (15, 15, 30, 210)
    COR_TITULO  = (255, 200, 50)
    COR_OK      = (80, 220, 80)
    COR_CARO    = (200, 80, 80)
    COR_MAX     = (120, 120, 120)
    COR_SEL     = (60, 80, 160)

    def __init__(self, tela):
        self.tela    = tela
        self.W, self.H = tela.get_size()
        self.visivel = False
        self.tipo    = None      
        self.sel     = 0         
        self._fonte_titulo = pygame.font.SysFont("monospace", 26, bold=True)
        self._fonte_item   = pygame.font.SysFont("monospace", 18, bold=True)
        self._fonte_desc   = pygame.font.SysFont("monospace", 14)
        self._fonte_custo  = pygame.font.SysFont("monospace", 14)
        
        # Guarda o retângulo do botão de sair para clique do mouse
        self.btn_sair_rect = None

    def abrir(self, tipo):
        self.visivel, self.tipo, self.sel = True, tipo, 0

    def fechar(self): 
        self.visivel, self.tipo = False, None

    def _upgrades(self): return UPGRADES_FERREIRO if self.tipo == "ferreiro" else UPGRADES_AMBULANTE

    def _pode_comprar(self, upgrade, inventario, player):
        # consumivel (tipo a pocao de cura) nao tem "nivel maximo", pode comprar de novo
        # sempre. so trava se o player ja ta com hp cheio (senao ia gastar recurso a toa)
        if upgrade.get("consumivel"):
            if player.hp >= player.hp_max: return False, "HP CHEIO"
            for item, qtd in upgrade["custo"].items():
                if not inventario.tem(item, qtd): return False, "SEM RECURSOS"
            return True, "COMPRAR"

        if self._nivel_atual(upgrade, player) >= upgrade["max"]: return False, "MAX"
        for item, qtd in upgrade["custo"].items():
            if not inventario.tem(item, qtd): return False, "SEM RECURSOS"
        return True, "COMPRAR"

    def _nivel_atual(self, upgrade, player): return getattr(player, upgrade["attr"], 0)

    def handle_event(self, event, inventario, player):
        if not self.visivel: return
        upgrades = self._upgrades()
        
        # Detecção por teclado
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_e): 
                self.fechar()
            elif event.key == pygame.K_UP: self.sel = (self.sel - 1) % len(upgrades)
            elif event.key == pygame.K_DOWN: self.sel = (self.sel + 1) % len(upgrades)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE): self._comprar(upgrades[self.sel], inventario, player)
            
        # CORREÇÃO: Detecção por clique do mouse no botão Sair
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_sair_rect and self.btn_sair_rect.collidepoint(event.pos):
                self.fechar()

    def _comprar(self, upgrade, inventario, player):
        pode, _ = self._pode_comprar(upgrade, inventario, player)
        if not pode: return
        for item, qtd in upgrade["custo"].items(): inventario.remover(item, qtd)

        attr = upgrade["attr"]
        if attr == "nivel_hp":
            player.nivel_hp += 1
            player.aumentar_hp_max(25)
        elif attr == "nivel_velocidade":
            player.nivel_velocidade += 1
            player.velocidade += 1
        elif attr == "nivel_forca":
            player.nivel_forca += 1
            player.DANO_PICARETA_PADRAO = 2 + player.nivel_forca * 2
        elif attr == "nivel_bomba_alcance": player.nivel_bomba_alcance += 1
        elif attr == "nivel_bomba_cd":
            player.nivel_bomba_cd += 1
            player.BOMBA_COOLDOWN_BASE = max(60, player.BOMBA_COOLDOWN_BASE - 30)
        elif attr == "nivel_bombas_simult":
            player.nivel_bombas_simult = 1
            player.max_bombas = 2
        elif attr == "imune_veneno": player.imune_veneno = True
        elif attr == "nivel_escudo":
            player.nivel_escudo += 1
            player.escudo_cargas += 1
        elif attr == "curar_hp":
            player.curar(60)  # recupera hp na hora, nao mexe no hp_max
        print(f"[LOJA] Comprou: {upgrade['nome']}")

    def draw(self, inventario, player):
        if not self.visivel: return
        upgrades = self._upgrades()
        nome_loja = "Ferreiro" if self.tipo == "ferreiro" else "Ambulante Mistico"

        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill(self.COR_FUNDO)
        self.tela.blit(overlay, (0, 0))

        pw, ph = 700, 500
        px, py = (self.W - pw) // 2, (self.H - ph) // 2
        pygame.draw.rect(self.tela, (20, 20, 45), (px, py, pw, ph), border_radius=10)
        pygame.draw.rect(self.tela, (80, 80, 160), (px, py, pw, ph), 2, border_radius=10)

        titulo = self._fonte_titulo.render(f"[ {nome_loja} ]", True, self.COR_TITULO)
        self.tela.blit(titulo, (px + pw // 2 - titulo.get_width() // 2, py + 16))

        # CORREÇÃO: Desenha botão visual de Sair ("X") para clique do mouse
        self.btn_sair_rect = pygame.Rect(px + pw - 110, py + 16, 90, 30)
        pygame.draw.rect(self.tela, (150, 40, 40), self.btn_sair_rect, border_radius=5)
        txt_sair = self._fonte_desc.render("❌ SAIR", True, (255, 255, 255))
        self.tela.blit(txt_sair, (self.btn_sair_rect.x + 15, self.btn_sair_rect.y + 6))

        for i, upg in enumerate(upgrades):
            iy = py + 90 + i * 88
            selecionado = (i == self.sel)
            pode, status = self._pode_comprar(upg, inventario, player)
            nivel = self._nivel_atual(upg, player)

            fundo_cor = self.COR_SEL if selecionado else (30, 30, 60)
            pygame.draw.rect(self.tela, fundo_cor, (px + 10, iy, pw - 20, 78), border_radius=6)

            nome_txt = self._fonte_item.render(f"{upg['icone']}  {upg['nome']}", True, (220, 220, 255))
            self.tela.blit(nome_txt, (px + 22, iy + 8))

            if upg.get("consumivel"):
                # consumivel nao tem "nivel", entao so mostra a descricao (maior, sem os quadradinhos)
                self.tela.blit(self._fonte_desc.render(upg["desc"], True, (160, 220, 160)), (px + 22, iy + 40))
            else:
                nivel_str = f"Nível: {'■' * nivel}{'□' * (upg['max'] - nivel)}"
                self.tela.blit(self._fonte_desc.render(nivel_str, True, (160, 200, 160)), (px + 22, iy + 32))
                self.tela.blit(self._fonte_desc.render(upg["desc"], True, (160, 160, 200)), (px + 22, iy + 50))

            custo_parts = [f"{item}:{inventario.itens.get(item,0)}/{qtd}" for item, qtd in upg["custo"].items()]
            cheio = upg.get("consumivel") and player.hp >= player.hp_max
            cor_custo = self.COR_OK if pode else (self.COR_MAX if (nivel >= upg["max"] or cheio) else self.COR_CARO)
            
            custo_txt = self._fonte_custo.render("  ".join(custo_parts), True, cor_custo)
            self.tela.blit(custo_txt, (px + pw - custo_txt.get_width() - 20, iy + 10))
            self.tela.blit(self._fonte_custo.render(f"[ {status} ]", True, cor_custo), (px + pw - 120, iy + 32))
