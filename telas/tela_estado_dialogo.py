import pygame
from telas.tela_estado_game import EstadoGame
from telas.estilo import fonte, painel, PAPEL, TEXTO_FRACO, MADEIRA, COBRE, OURO


class EstadoDialogo(EstadoGame):
    def __init__(self, gerenciador, npc):
        super().__init__(gerenciador)
        self.npc = npc
        self.fonte_nome = fonte(25, True, True)
        self.fonte_texto = fonte(19)
        self.fonte_dica = fonte(14)

        if npc.tipo == "ferreiro":
            self.falas = [
                "Ora, ora... olha só quem voltou da mina. Tem coisa boa na mochila?",
                "Posso dar um trato na sua picareta e melhorar suas bombas. Só não espere desconto: metal não se trabalha sozinho.",
                "Dê uma olhada no que consigo fazer. Se tiver os materiais, a gente fecha negócio.",
            ]
        else:
            self.falas = [
                "Chegue mais perto. Essas cavernas guardam coisas que nem todo mundo consegue enxergar.",
                "Trago comigo alguns preparados. Essências, gosmas... tudo pode ter sua utilidade nas mãos certas.",
                "Veja o que tenho hoje. Talvez encontre algo que ajude na próxima descida.",
            ]
        self.indice = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.indice += 1
                if self.indice >= len(self.falas):
                    self.gerenciador.game.tela_loja.abrir(self.npc.tipo)
                    self.gerenciador.mudar_estado_imediato("loja")
            elif event.key == pygame.K_ESCAPE:
                self.gerenciador.mudar_estado_imediato("jogo")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.indice += 1
            if self.indice >= len(self.falas):
                self.gerenciador.game.tela_loja.abrir(self.npc.tipo)
                self.gerenciador.mudar_estado_imediato("loja")

    def desenhar(self, tela):
        self.gerenciador.estados_registrados["jogo"].desenhar(tela)
        largura = min(980, tela.get_width() - 80)
        altura = 205
        x = (tela.get_width() - largura) // 2
        y = tela.get_height() - altura - 35
        caixa = pygame.Rect(x, y, largura, altura)
        painel(tela, caixa, (31, 27, 22), self.npc.cor, 12)

        # A pequena faixa lateral ajuda a separar o retrato/nome da fala.
        pygame.draw.rect(tela, self.npc.cor, (x, y, 9, altura), border_radius=5)
        nome = self.fonte_nome.render(self.npc.nome, True, self.npc.cor)
        tela.blit(nome, (x + 32, y + 22))
        tipo = 'FERREIRO' if self.npc.tipo == 'ferreiro' else 'VIAJANTE'
        etiqueta = fonte(12, True).render(tipo, True, TEXTO_FRACO)
        tela.blit(etiqueta, (x + 34, y + 57))
        pygame.draw.line(tela, (83, 68, 51), (x + 32, y + 83), (x + largura - 32, y + 83), 1)

        fala = self.falas[self.indice]
        area = pygame.Rect(x + 32, y + 103, largura - 64, 57)
        palavras = fala.split()
        linhas = []
        linha = ''
        for palavra in palavras:
            teste = palavra if not linha else linha + ' ' + palavra
            if self.fonte_texto.size(teste)[0] <= area.width:
                linha = teste
            else:
                if linha:
                    linhas.append(linha)
                linha = palavra
        if linha:
            linhas.append(linha)
        for i, texto in enumerate(linhas[:2]):
            imagem = self.fonte_texto.render(texto, True, PAPEL)
            tela.blit(imagem, (area.x, area.y + i * 27))

        dica = self.fonte_dica.render('ESPAÇO  continuar', True, OURO)
        sair = self.fonte_dica.render('ESC  sair', True, TEXTO_FRACO)
        tela.blit(dica, (x + largura - dica.get_width() - 32, y + altura - 28))
        tela.blit(sair, (x + 32, y + altura - 28))
