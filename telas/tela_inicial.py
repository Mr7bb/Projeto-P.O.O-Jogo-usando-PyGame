import pygame
from telas.estilo import fonte, fundo_pedra, painel, CARVAO, PEDRA, MADEIRA, COBRE, OURO, PAPEL, TEXTO_FRACO


class TelaInicial:
    def __init__(self, tela):
        self.tela = tela
        self.largura, self.altura = tela.get_size()
        self.fonte_titulo = fonte(68, True, True)
        self.fonte_sub = fonte(19)
        self.fonte_menu = fonte(29, True)
        self.fonte_dica = fonte(15)
        self.fonte_pequena = fonte(13, True)
        self.opcoes = ["JOGAR", "CRÉDITOS", "SAIR"]
        self.selecionado = 0
        self.tick = 0
        self.botao_rects = []
        self.mostrar_creditos = False

    def handle_event(self, event):
        if self.mostrar_creditos:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE):
                self.mostrar_creditos = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mostrar_creditos = False
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selecionado = (self.selecionado - 1) % len(self.opcoes)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selecionado = (self.selecionado + 1) % len(self.opcoes)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                acao = self.opcoes[self.selecionado]
                if acao == "CRÉDITOS":
                    self.mostrar_creditos = True
                    return None
                return "CREDITOS" if acao == "CRÉDITOS" else acao

        if event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.botao_rects):
                if rect.collidepoint(event.pos):
                    self.selecionado = i
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.botao_rects):
                if rect.collidepoint(event.pos):
                    acao = self.opcoes[i]
                    if acao == "CRÉDITOS":
                        self.mostrar_creditos = True
                        return None
                    return acao
        return None

    def draw(self):
        self.tick += 1
        fundo_pedra(self.tela)
        if self.mostrar_creditos:
            self._desenhar_creditos()
            return

        # Mancha de luz atrás da marca do jogo.
        luz = pygame.Surface((470, 470), pygame.SRCALPHA)
        pygame.draw.circle(luz, (151, 91, 39, 24), (235, 235), 225)
        self.tela.blit(luz, (self.largura // 2 - 235, 10))

        # Painel lateral com a marca, separado do menu.
        painel_esq = pygame.Rect(105, 115, 560, 625)
        painel(self.tela, painel_esq, (29, 25, 21), (112, 75, 43), 14)
        marca = self.fonte_pequena.render('COMPANHIA DE EXPLORAÇÃO', True, COBRE)
        self.tela.blit(marca, (150, 165))
        titulo = self.fonte_titulo.render('BLAST', True, OURO)
        titulo2 = self.fonte_titulo.render('MINER', True, PAPEL)
        self.tela.blit(titulo, (145, 235))
        self.tela.blit(titulo2, (145, 300))
        pygame.draw.rect(self.tela, COBRE, (150, 390, 300, 3))
        subtitulo = self.fonte_sub.render('O que existe abaixo da pedra?', True, TEXTO_FRACO)
        self.tela.blit(subtitulo, (150, 415))

        # Pequeno desenho de picareta e minério feito com formas simples.
        pygame.draw.circle(self.tela, (87, 68, 48), (475, 570), 72)
        pygame.draw.circle(self.tela, (132, 99, 59), (475, 570), 72, 2)
        pygame.draw.line(self.tela, (145, 94, 48), (430, 620), (515, 510), 13)
        pygame.draw.line(self.tela, (205, 183, 145), (415, 525), (535, 535), 13)
        pygame.draw.line(self.tela, (205, 183, 145), (415, 525), (440, 495), 13)
        pygame.draw.circle(self.tela, OURO, (530, 600), 8)
        pygame.draw.circle(self.tela, (118, 161, 115), (420, 585), 6)

        menu = pygame.Rect(735, 235, 350, 390)
        painel(self.tela, menu, (38, 32, 26), (91, 70, 49), 12)
        cabecalho = self.fonte_pequena.render('PRÓXIMA EXPEDIÇÃO', True, TEXTO_FRACO)
        self.tela.blit(cabecalho, (menu.x + 34, menu.y + 34))
        self.botao_rects = []
        mx, my = pygame.mouse.get_pos()
        for i, opcao in enumerate(self.opcoes):
            rect = pygame.Rect(menu.x + 25, menu.y + 90 + i * 78, menu.width - 50, 58)
            self.botao_rects.append(rect)
            ativo = i == self.selecionado or rect.collidepoint(mx, my)
            if ativo:
                pygame.draw.rect(self.tela, (82, 57, 34), rect, border_radius=7)
                pygame.draw.rect(self.tela, OURO, rect, 2, border_radius=7)
                cor = OURO
                pygame.draw.polygon(self.tela, OURO, [(rect.x + 15, rect.centery), (rect.x + 23, rect.centery - 6), (rect.x + 23, rect.centery + 6)])
            else:
                pygame.draw.line(self.tela, (78, 65, 51), (rect.x + 8, rect.bottom), (rect.right - 8, rect.bottom), 1)
                cor = PAPEL
            texto = self.fonte_menu.render(opcao, True, cor)
            self.tela.blit(texto, (rect.x + 43, rect.centery - texto.get_height() // 2))

        rodape = self.fonte_dica.render('↑ ↓  escolher     ENTER  entrar', True, TEXTO_FRACO)
        self.tela.blit(rodape, rodape.get_rect(center=(self.largura // 2, self.altura - 55)))
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if any(r.collidepoint(mx, my) for r in self.botao_rects) else pygame.SYSTEM_CURSOR_ARROW)

    def _desenhar_creditos(self):
        caixa = pygame.Rect(190, 170, self.largura - 380, self.altura - 340)
        painel(self.tela, caixa, (34, 29, 24), (150, 103, 56), 12)
        titulo = self.fonte_titulo.render('Créditos', True, OURO)
        self.tela.blit(titulo, titulo.get_rect(center=(self.largura // 2, caixa.y + 90)))
        linhas = [
            'BLAST MINER Co.',
            'Feito por Marcos e Apolo.',
            'Um projeto de exploração, combate e descoberta.',
            'Desenvolvido em Python com Pygame.',
        ]
        for i, linha in enumerate(linhas):
            imagem = self.fonte_sub.render(linha, True, PAPEL if i < 2 else TEXTO_FRACO)
            self.tela.blit(imagem, imagem.get_rect(center=(self.largura // 2, caixa.y + 205 + i * 43)))
        dica = self.fonte_dica.render('ESC ou clique para voltar', True, TEXTO_FRACO)
        self.tela.blit(dica, dica.get_rect(center=(self.largura // 2, caixa.bottom - 42)))
