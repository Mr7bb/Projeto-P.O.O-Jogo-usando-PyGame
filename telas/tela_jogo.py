import pygame
from telas.estilo import fonte, painel, PEDRA, COBRE, OURO, PAPEL, TEXTO_FRACO


class TelaPause:
    def __init__(self, tela):
        self.tela = tela
        self.largura, self.altura = tela.get_size()
        self.fonte_titulo = fonte(48, True, True)
        self.fonte_menu = fonte(25, True)
        self.fonte_dica = fonte(14)
        self.opcoes = ["CONTINUAR", "MENU PRINCIPAL", "SAIR"]
        self.selecionado = 0
        self.botao_rects = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "CONTINUAR"
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selecionado = (self.selecionado - 1) % len(self.opcoes)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selecionado = (self.selecionado + 1) % len(self.opcoes)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.opcoes[self.selecionado]
        if event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.botao_rects):
                if rect.collidepoint(event.pos):
                    self.selecionado = i
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.botao_rects):
                if rect.collidepoint(event.pos):
                    return self.opcoes[i]
        return None

    def draw(self):
        sombra = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        sombra.fill((8, 7, 6, 190))
        self.tela.blit(sombra, (0, 0))
        caixa = pygame.Rect(self.largura // 2 - 235, self.altura // 2 - 230, 470, 460)
        painel(self.tela, caixa, (35, 29, 23), (155, 105, 55), 13)
        etiqueta = fonte(13, True).render('EXPEDIÇÃO INTERROMPIDA', True, COBRE)
        self.tela.blit(etiqueta, etiqueta.get_rect(center=(caixa.centerx, caixa.y + 48)))
        titulo = self.fonte_titulo.render('Pausa', True, OURO)
        self.tela.blit(titulo, titulo.get_rect(center=(caixa.centerx, caixa.y + 112)))
        pygame.draw.line(self.tela, (91, 71, 49), (caixa.x + 45, caixa.y + 158), (caixa.right - 45, caixa.y + 158), 1)
        self.botao_rects = []
        mx, my = pygame.mouse.get_pos()
        for i, opcao in enumerate(self.opcoes):
            rect = pygame.Rect(caixa.x + 55, caixa.y + 190 + i * 70, caixa.width - 110, 52)
            self.botao_rects.append(rect)
            ativo = i == self.selecionado or rect.collidepoint(mx, my)
            if ativo:
                pygame.draw.rect(self.tela, (78, 55, 34), rect, border_radius=6)
                pygame.draw.rect(self.tela, OURO, rect, 2, border_radius=6)
            texto = self.fonte_menu.render(opcao, True, OURO if ativo else PAPEL)
            self.tela.blit(texto, texto.get_rect(center=rect.center))
        dica = self.fonte_dica.render('ESC volta para a exploração', True, TEXTO_FRACO)
        self.tela.blit(dica, dica.get_rect(center=(caixa.centerx, caixa.bottom - 27)))
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if any(r.collidepoint(mx, my) for r in self.botao_rects) else pygame.SYSTEM_CURSOR_ARROW)
