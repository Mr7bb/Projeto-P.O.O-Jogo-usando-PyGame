import pygame
from telas.estilo import fonte, fundo_pedra, painel, PAPEL, TEXTO_FRACO, VERMELHO, MADEIRA


class TelaGameOver:
    def __init__(self, tela):
        self.tela = tela
        self.largura, self.altura = tela.get_size()
        self.fonte_titulo = fonte(70, True, True)
        self.fonte_sub = fonte(19)
        self.fonte_menu = fonte(25, True)
        self.fonte_dica = fonte(14)
        self.opcoes = ["TENTAR NOVAMENTE", "MENU PRINCIPAL", "SAIR"]
        self.selecionado = 0
        self.botao_rects = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
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
        fundo_pedra(self.tela, -3)
        caixa = pygame.Rect(300, 105, self.largura - 600, self.altura - 210)
        painel(self.tela, caixa, (31, 24, 21), (126, 61, 48), 14)
        pygame.draw.circle(self.tela, (83, 37, 31), (self.largura // 2, 255), 76, 2)
        pygame.draw.line(self.tela, VERMELHO, (self.largura // 2 - 28, 227), (self.largura // 2 + 28, 283), 7)
        pygame.draw.line(self.tela, VERMELHO, (self.largura // 2 + 28, 227), (self.largura // 2 - 28, 283), 7)
        titulo = self.fonte_titulo.render('Fim da expedição', True, (207, 112, 91))
        self.tela.blit(titulo, titulo.get_rect(center=(self.largura // 2, 370)))
        subtitulo = self.fonte_sub.render('A mina ainda estará aqui quando você voltar.', True, TEXTO_FRACO)
        self.tela.blit(subtitulo, subtitulo.get_rect(center=(self.largura // 2, 425)))
        self.botao_rects = []
        mx, my = pygame.mouse.get_pos()
        for i, opcao in enumerate(self.opcoes):
            rect = pygame.Rect(self.largura // 2 - 190, 500 + i * 61, 380, 46)
            self.botao_rects.append(rect)
            ativo = i == self.selecionado or rect.collidepoint(mx, my)
            if ativo:
                pygame.draw.rect(self.tela, (78, 42, 34), rect, border_radius=6)
                pygame.draw.rect(self.tela, (207, 112, 91), rect, 2, border_radius=6)
            texto = self.fonte_menu.render(opcao, True, PAPEL if not ativo else (255, 191, 165))
            self.tela.blit(texto, texto.get_rect(center=rect.center))
        dica = self.fonte_dica.render('↑ ↓ escolher  ·  ENTER confirmar', True, TEXTO_FRACO)
        self.tela.blit(dica, dica.get_rect(center=(self.largura // 2, self.altura - 42)))
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if any(r.collidepoint(mx, my) for r in self.botao_rects) else pygame.SYSTEM_CURSOR_ARROW)
