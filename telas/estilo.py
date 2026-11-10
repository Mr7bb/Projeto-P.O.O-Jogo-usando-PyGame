import pygame

# Paleta usada pelas interfaces: pedra, madeira e cobre.
CARVAO = (19, 17, 16)
PEDRA = (34, 30, 26)
MADEIRA = (67, 45, 29)
COBRE = (190, 119, 57)
OURO = (231, 190, 105)
PAPEL = (229, 216, 187)
TEXTO_FRACO = (157, 147, 128)
VERDE = (135, 177, 111)
VERMELHO = (190, 83, 67)


def fonte(tamanho, negrito=False, serifada=False):
    nome = 'georgia' if serifada else 'trebuchet ms'
    return pygame.font.SysFont(nome, tamanho, bold=negrito)


def texto_quebrado(superficie, texto, fonte_texto, cor, area, espacamento=5):
    """Desenha um texto em várias linhas dentro de uma área e retorna a altura usada."""
    palavras = texto.split()
    linhas = []
    linha = ''
    for palavra in palavras:
        teste = palavra if not linha else linha + ' ' + palavra
        if fonte_texto.size(teste)[0] <= area.width:
            linha = teste
        else:
            if linha:
                linhas.append(linha)
            linha = palavra
    if linha:
        linhas.append(linha)

    y = area.y
    for linha in linhas:
        imagem = fonte_texto.render(linha, True, cor)
        superficie.blit(imagem, (area.x, y))
        y += imagem.get_height() + espacamento
    return y - area.y


def painel(superficie, rect, cor=PEDRA, borda=COBRE, raio=10):
    sombra = rect.move(0, 7)
    pygame.draw.rect(superficie, (8, 7, 6), sombra, border_radius=raio)
    pygame.draw.rect(superficie, cor, rect, border_radius=raio)
    pygame.draw.rect(superficie, borda, rect, 2, border_radius=raio)
    pygame.draw.line(superficie, tuple(min(255, c + 22) for c in cor),
                     (rect.x + 18, rect.y + 2), (rect.right - 18, rect.y + 2), 1)


def fundo_pedra(superficie, tom=0):
    superficie.fill((20 + tom, 18 + tom, 16 + tom))
    largura, altura = superficie.get_size()
    # Marcas discretas de pedra; sem a grade repetitiva das telas antigas.
    for y in range(24, altura, 96):
        pygame.draw.line(superficie, (27 + tom, 24 + tom, 21 + tom),
                         (0, y), (largura, y), 1)
    for x in range(38, largura, 173):
        pygame.draw.line(superficie, (25 + tom, 22 + tom, 19 + tom),
                         (x, 0), (x, altura), 1)
