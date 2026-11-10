import pygame
from telas.estilo import fonte, painel, PAPEL, TEXTO_FRACO, OURO, VERDE, VERMELHO, MADEIRA, COBRE

UPGRADES_FERREIRO = [
    {'nome': 'Força da Picareta', 'attr': 'nivel_forca', 'custo': {'Minerio Comum': 2, 'Cristais': 1}, 'max': 5, 'icone': 'PIC', 'desc': 'A picareta causa mais dano.'},
    {'nome': 'Alcance da Bomba', 'attr': 'nivel_bomba_alcance', 'custo': {'Minerio Comum': 2, 'Madeira': 2}, 'max': 3, 'icone': 'BOM', 'desc': 'A explosão alcança uma área maior.'},
    {'nome': 'Pavio mais rápido', 'attr': 'nivel_bomba_cd', 'custo': {'Madeira': 3, 'Minerio Raro': 1}, 'max': 3, 'icone': 'PAV', 'desc': 'Reduz o tempo entre uma bomba e outra.'},
    {'nome': 'Segunda Bomba', 'attr': 'nivel_bombas_simult', 'custo': {'Minerio Raro': 2, 'Cristais': 2}, 'max': 1, 'icone': '2X', 'desc': 'Permite deixar duas bombas no campo.'},
]

UPGRADES_AMBULANTE = [
    {'nome': 'Vida Extra', 'attr': 'nivel_hp', 'custo': {'Essencia Fantasmal': 1, 'Gosma': 2}, 'max': 5, 'icone': 'VID', 'desc': 'Aumenta sua vida máxima em 25.'},
    {'nome': 'Velocidade', 'attr': 'nivel_velocidade', 'custo': {'Esporos': 2, 'Musgo': 2}, 'max': 4, 'icone': 'VEL', 'desc': 'Melhora a velocidade de movimento.'},
    {'nome': 'Imunidade a Veneno', 'attr': 'imune_veneno', 'custo': {'Nucleo de Esporos': 1, 'Chapeu de Cogumelo': 1}, 'max': 1, 'icone': 'VEN', 'desc': 'Impede que novos venenos façam efeito.'},
    {'nome': 'Escudo Temporário', 'attr': 'nivel_escudo', 'custo': {'Gosma': 2, 'Musgo': 1, 'Olho de Goblin': 1}, 'max': 3, 'icone': 'ESC', 'desc': 'Ganha uma carga para absorver um golpe.'},
    {'nome': 'Poção de Cura', 'attr': 'curar_hp', 'custo': {'Gosma': 1, 'Esporos': 1}, 'max': 1, 'icone': 'HP+', 'desc': 'Recupera 60 pontos de vida.', 'consumivel': True},
]


class TelaLoja:
    def __init__(self, tela):
        self.tela = tela
        self.W, self.H = tela.get_size()
        self.visivel = False
        self.tipo = None
        self.sel = 0
        self.fonte_titulo = fonte(35, True, True)
        self.fonte_item = fonte(20, True)
        self.fonte_desc = fonte(15)
        self.fonte_custo = fonte(13)
        self.fonte_dica = fonte(13)
        self.btn_sair_rect = None
        self.item_rects = []

    def abrir(self, tipo):
        self.visivel, self.tipo, self.sel = True, tipo, 0

    def fechar(self):
        self.visivel, self.tipo = False, None

    def _upgrades(self):
        return UPGRADES_FERREIRO if self.tipo == 'ferreiro' else UPGRADES_AMBULANTE

    def _nivel_atual(self, upgrade, player):
        return getattr(player, upgrade['attr'], 0)

    def _pode_comprar(self, upgrade, inventario, player):
        if upgrade.get('consumivel') and player.hp >= player.hp_max:
            return False, 'VIDA CHEIA'
        if not upgrade.get('consumivel') and self._nivel_atual(upgrade, player) >= upgrade['max']:
            return False, 'NO MÁXIMO'
        for item, qtd in upgrade['custo'].items():
            if not inventario.tem(item, qtd):
                return False, 'FALTAM MATERIAIS'
        return True, 'DISPONÍVEL'

    def handle_event(self, event, inventario, player):
        if not self.visivel:
            return
        upgrades = self._upgrades()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_e):
                self.fechar()
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(upgrades)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(upgrades)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._comprar(upgrades[self.sel], inventario, player)
        elif event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(event.pos):
                    self.sel = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_sair_rect and self.btn_sair_rect.collidepoint(event.pos):
                self.fechar()
            else:
                for i, rect in enumerate(self.item_rects):
                    if rect.collidepoint(event.pos):
                        self.sel = i
                        self._comprar(upgrades[i], inventario, player)
                        break

    def _comprar(self, upgrade, inventario, player):
        pode, _ = self._pode_comprar(upgrade, inventario, player)
        if not pode:
            return
        for item, qtd in upgrade['custo'].items():
            inventario.remover(item, qtd)
        attr = upgrade['attr']
        if attr == 'nivel_hp':
            player.nivel_hp += 1
            player.aumentar_hp_max(25)
        elif attr == 'nivel_velocidade':
            player.nivel_velocidade += 1
            player.velocidade += 1
        elif attr == 'nivel_forca':
            player.nivel_forca += 1
        elif attr == 'nivel_bomba_alcance':
            player.nivel_bomba_alcance += 1
        elif attr == 'nivel_bomba_cd':
            player.nivel_bomba_cd += 1
            player.BOMBA_COOLDOWN_BASE = max(60, player.BOMBA_COOLDOWN_BASE - 30)
        elif attr == 'nivel_bombas_simult':
            player.nivel_bombas_simult = 1
            player.max_bombas = 2
        elif attr == 'imune_veneno':
            player.imune_veneno = True
        elif attr == 'nivel_escudo':
            player.nivel_escudo += 1
            player.escudo_cargas += 1
        elif attr == 'curar_hp':
            player.curar(60)

    def draw(self, inventario, player):
        if not self.visivel:
            return
        upgrades = self._upgrades()
        overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        overlay.fill((8, 7, 6, 205))
        self.tela.blit(overlay, (0, 0))

        caixa = pygame.Rect(145, 85, self.W - 290, self.H - 170)
        painel(self.tela, caixa, (34, 29, 23), (139, 96, 53), 13)
        nome_loja = 'Oficina do Ferreiro' if self.tipo == 'ferreiro' else 'Banca do Viajante'
        subtitulo = 'Melhorias feitas à mão' if self.tipo == 'ferreiro' else 'Preparos e achados de outras cavernas'
        titulo = self.fonte_titulo.render(nome_loja, True, OURO)
        self.tela.blit(titulo, (caixa.x + 34, caixa.y + 22))
        sub = self.fonte_desc.render(subtitulo, True, TEXTO_FRACO)
        self.tela.blit(sub, (caixa.x + 37, caixa.y + 67))

        self.btn_sair_rect = pygame.Rect(caixa.right - 112, caixa.y + 28, 78, 34)
        pygame.draw.rect(self.tela, (76, 48, 34), self.btn_sair_rect, border_radius=5)
        pygame.draw.rect(self.tela, (143, 92, 57), self.btn_sair_rect, 1, border_radius=5)
        sair = self.fonte_custo.render('FECHAR  X', True, PAPEL)
        self.tela.blit(sair, sair.get_rect(center=self.btn_sair_rect.center))
        pygame.draw.line(self.tela, (86, 68, 48), (caixa.x + 30, caixa.y + 105), (caixa.right - 30, caixa.y + 105), 1)

        self.item_rects = []
        mx, my = pygame.mouse.get_pos()
        altura_item = 105 if len(upgrades) == 4 else 91
        inicio_y = caixa.y + 125
        for i, upg in enumerate(upgrades):
            iy = inicio_y + i * altura_item
            rect = pygame.Rect(caixa.x + 28, iy, caixa.width - 56, altura_item - 10)
            self.item_rects.append(rect)
            ativo = i == self.sel or rect.collidepoint(mx, my)
            pode, status = self._pode_comprar(upg, inventario, player)
            nivel = self._nivel_atual(upg, player)
            fundo = (68, 51, 34) if ativo else (43, 37, 29)
            pygame.draw.rect(self.tela, fundo, rect, border_radius=7)
            pygame.draw.rect(self.tela, OURO if ativo else (83, 69, 51), rect, 2 if ativo else 1, border_radius=7)

            icone_rect = pygame.Rect(rect.x + 14, rect.y + 17, 48, 48)
            pygame.draw.rect(self.tela, (87, 62, 37), icone_rect, border_radius=6)
            icone = fonte(13, True).render(upg['icone'], True, OURO)
            self.tela.blit(icone, icone.get_rect(center=icone_rect.center))

            nome = self.fonte_item.render(upg['nome'], True, PAPEL)
            self.tela.blit(nome, (rect.x + 78, rect.y + 12))
            desc = self.fonte_desc.render(upg['desc'], True, TEXTO_FRACO)
            self.tela.blit(desc, (rect.x + 78, rect.y + 43))
            if not upg.get('consumivel'):
                nivel_txt = self.fonte_custo.render(f'NÍVEL {nivel}/{upg["max"]}', True, VERDE if nivel < upg['max'] else TEXTO_FRACO)
                self.tela.blit(nivel_txt, (rect.x + 78, rect.y + 67))

            custo = '  ·  '.join(f'{item}: {inventario.itens.get(item, 0)}/{qtd}' for item, qtd in upg['custo'].items())
            custo_txt = self.fonte_custo.render(custo, True, VERDE if pode else VERMELHO)
            self.tela.blit(custo_txt, (rect.right - custo_txt.get_width() - 15, rect.y + 17))
            estado = self.fonte_custo.render('COMPRAR' if pode else status, True, VERDE if pode else VERMELHO)
            self.tela.blit(estado, (rect.right - estado.get_width() - 15, rect.y + 48))

        dica = self.fonte_dica.render('↑ ↓ escolher   ·   ENTER comprar   ·   E ou ESC sair', True, TEXTO_FRACO)
        self.tela.blit(dica, dica.get_rect(center=(caixa.centerx, caixa.bottom - 23)))
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if self.btn_sair_rect.collidepoint(mx, my) or any(r.collidepoint(mx, my) for r in self.item_rects) else pygame.SYSTEM_CURSOR_ARROW)
