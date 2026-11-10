import pygame
from telas.estilo import fonte, fundo_pedra, painel, OURO, PAPEL, TEXTO_FRACO, VERDE


class TelaVitoria:
    def __init__(self, tela):
        self.tela = tela
        self.largura, self.altura = tela.get_size()
        self.fonte_titulo = fonte(57, True, True)
        self.fonte_subtitulo = fonte(22, True)
        self.fonte_texto = fonte(18)
        self.fonte_dica = fonte(14)

    def draw(self):
        fundo_pedra(self.tela, 1)
        caixa = pygame.Rect(170, 125, self.largura - 340, self.altura - 250)
        painel(self.tela, caixa, (30, 34, 27), (126, 145, 85), 14)
        # Um brilho discreto para marcar o Coração da Mina como conquista.
        centro = (self.largura // 2, 270)
        pygame.draw.circle(self.tela, (91, 116, 69), centro, 68, 2)
        pygame.draw.circle(self.tela, (151, 177, 105), centro, 48, 2)
        pygame.draw.polygon(self.tela, OURO, [(centro[0], centro[1] - 31), (centro[0] + 25, centro[1]), (centro[0], centro[1] + 31), (centro[0] - 25, centro[1])])
        titulo = self.fonte_titulo.render('A mina está em paz', True, (190, 213, 145))
        self.tela.blit(titulo, titulo.get_rect(center=(self.largura // 2, 390)))
        subtitulo = self.fonte_subtitulo.render('O Coração da Mina foi derrotado.', True, OURO)
        self.tela.blit(subtitulo, subtitulo.get_rect(center=(self.largura // 2, 455)))
        texto = self.fonte_texto.render('Sua jornada chegou ao fim. Obrigado por explorar.', True, PAPEL)
        self.tela.blit(texto, texto.get_rect(center=(self.largura // 2, 510)))
        dica = self.fonte_dica.render('ENTER, ESPAÇO ou clique para voltar ao menu', True, TEXTO_FRACO)
        self.tela.blit(dica, dica.get_rect(center=(self.largura // 2, 625)))
