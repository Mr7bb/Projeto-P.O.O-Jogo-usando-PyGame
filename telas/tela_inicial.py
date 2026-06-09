import pygame


class TelaInicial:
    def __init__(self, tela):
        self.tela = tela
        self.largura = tela.get_width()
        self.altura  = tela.get_height()

        self.fonte_titulo = pygame.font.SysFont("monospace", 64, bold=True)
        self.fonte_sub    = pygame.font.SysFont("monospace", 22)
        self.fonte_menu   = pygame.font.SysFont("monospace", 36, bold=True)
        self.fonte_dica   = pygame.font.SysFont("monospace", 18)

        self.opcoes      = ["JOGAR", "CREDITOS", "SAIR"]
        self.selecionado = 0
        self.tick        = 0  # contador para animações

        # rects dos botões calculados no draw() e guardados aqui
        self.botao_rects = []

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selecionado = (self.selecionado - 1) % len(self.opcoes)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selecionado = (self.selecionado + 1) % len(self.opcoes)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.opcoes[self.selecionado]

        # hover com o mouse
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, rect in enumerate(self.botao_rects):
                if rect.collidepoint(mx, my):
                    self.selecionado = i

        # clique do mouse
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, rect in enumerate(self.botao_rects):
                if rect.collidepoint(mx, my):
                    return self.opcoes[i]

        return None

    def draw(self):
        self.tick += 1
        self.tela.fill((15, 15, 20))

       
        for x in range(0, self.largura, 50):
            pygame.draw.line(self.tela, (25, 25, 35), (x, 0), (x, self.altura))
        for y in range(0, self.altura, 50):
            pygame.draw.line(self.tela, (25, 25, 35), (0, y), (self.largura, y))

        # ── título 
        brilho = int(200 + 55 * abs(pygame.math.Vector2(1, 0).rotate(self.tick * 2).x))
        cor_titulo = (brilho, int(brilho * 0.78), 0)

        titulo  = self.fonte_titulo.render("BLAST MINER Co.", True, cor_titulo)
        tx      = self.largura  // 2 - titulo.get_width()  // 2
        self.tela.blit(titulo, (tx, 100))

        # sublinhado amarelo
        pygame.draw.rect(self.tela, (255, 200, 0),
                         (tx, 100 + titulo.get_height() + 4, titulo.get_width(), 3))


        # ── ícone de bomba 
        cx, cy = self.largura // 2, 270
        pygame.draw.circle(self.tela, (50, 50, 60), (cx, cy), 30)
        pygame.draw.circle(self.tela, (80, 80, 90), (cx, cy), 30, 3)
        pygame.draw.line(self.tela, (255, 200, 0), (cx + 20, cy - 20), (cx + 35, cy - 35), 3)
        pygame.draw.circle(self.tela, (255, 150, 0), (cx + 36, cy - 36), 5)

        # ── opções do menu ─
        self.botao_rects = []
        box_w = 260
        box_x = self.largura // 2 - box_w // 2
        mx, my = pygame.mouse.get_pos()

        for i, opcao in enumerate(self.opcoes):
            y_pos = 340 + i * 70
            rect  = pygame.Rect(box_x, y_pos - 10, box_w, 52)
            self.botao_rects.append(rect)

            hover      = rect.collidepoint(mx, my)
            selecionado = i == self.selecionado or hover

            if selecionado:
                pygame.draw.rect(self.tela, (40, 38, 10), rect, border_radius=6)
                pygame.draw.rect(self.tela, (255, 200, 0), rect, 2, border_radius=6)
                cor     = (255, 200, 0)
                prefixo = "> "
            else:
                cor     = (130, 130, 150)
                prefixo = "  "

            texto = self.fonte_menu.render(prefixo + opcao, True, cor)
            self.tela.blit(texto, (self.largura // 2 - texto.get_width() // 2, y_pos))

        # cursor vira mãozinha 
        sobre_botao = any(r.collidepoint(mx, my) for r in self.botao_rects)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if sobre_botao
                                else pygame.SYSTEM_CURSOR_ARROW)

        # ── dica de navegação
        dica = self.fonte_dica.render("↑ ↓  navegar    ENTER  confirmar    🖱 clique", True, (55, 55, 70))
        self.tela.blit(dica, (self.largura // 2 - dica.get_width() // 2, self.altura - 40))

        pygame.display.flip()