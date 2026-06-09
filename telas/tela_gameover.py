import pygame


class TelaGameOver:
    def __init__(self, tela):
        self.tela    = tela
        self.largura = tela.get_width()
        self.altura  = tela.get_height()

        self.fonte_titulo = pygame.font.SysFont("monospace", 72, bold=True)
        self.fonte_sub    = pygame.font.SysFont("monospace", 22)
        self.fonte_menu   = pygame.font.SysFont("monospace", 32, bold=True)
        self.fonte_dica   = pygame.font.SysFont("monospace", 16)

        self.opcoes      = ["TENTAR NOVAMENTE", "MENU PRINCIPAL", "SAIR"]
        self.selecionado = 0
        self.botao_rects = []
        self.tick        = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selecionado = (self.selecionado - 1) % len(self.opcoes)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selecionado = (self.selecionado + 1) % len(self.opcoes)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.opcoes[self.selecionado]

        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for i, rect in enumerate(self.botao_rects):
                if rect.collidepoint(mx, my):
                    self.selecionado = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, rect in enumerate(self.botao_rects):
                if rect.collidepoint(mx, my):
                    return self.opcoes[i]

        return None

    def draw(self):
        self.tick += 1
        self.tela.fill((10, 5, 5))

        # ── grade vermelha de fundo ────────────────────────────────────────
        for x in range(0, self.largura, 50):
            pygame.draw.line(self.tela, (30, 10, 10), (x, 0), (x, self.altura))
        for y in range(0, self.altura, 50):
            pygame.draw.line(self.tela, (30, 10, 10), (0, y), (self.largura, y))

        # ── título GAME OVER ───────────────────────────────────────────────
        brilho = int(180 + 75 * abs(pygame.math.Vector2(1, 0).rotate(self.tick * 2).x))
        titulo = self.fonte_titulo.render("GAME OVER", True, (brilho, 0, 0))
        tx = self.largura // 2 - titulo.get_width() // 2
        self.tela.blit(titulo, (tx, 80))

        # sublinhado vermelho
        pygame.draw.rect(self.tela, (180, 0, 0),
                         (tx, 80 + titulo.get_height() + 4, titulo.get_width(), 3))

        # subtítulo
        sub = self.fonte_sub.render("CONTRATO RESCINDIDO", True, (100, 40, 40))
        self.tela.blit(sub, (self.largura // 2 - sub.get_width() // 2, 185))

    

        # ── botões 
        self.botao_rects = []
        btn_w = 300
        btn_x = self.largura // 2 - btn_w // 2
        mx, my = pygame.mouse.get_pos()

        for i, opcao in enumerate(self.opcoes):
            y_pos = 330 + i * 65
            rect  = pygame.Rect(btn_x, y_pos, btn_w, 48)
            self.botao_rects.append(rect)

            hover = rect.collidepoint(mx, my)
            ativo = i == self.selecionado or hover

            if ativo:
                pygame.draw.rect(self.tela, (40, 5, 5), rect, border_radius=6)
                pygame.draw.rect(self.tela, (200, 0, 0), rect, 2, border_radius=6)
                cor     = (255, 60, 60)
                prefixo = "> "
            else:
                cor     = (110, 50, 50)
                prefixo = "  "

            texto = self.fonte_menu.render(prefixo + opcao, True, cor)
            self.tela.blit(texto, (self.largura // 2 - texto.get_width() // 2, y_pos + 8))

        # cursor
        sobre_botao = any(r.collidepoint(mx, my) for r in self.botao_rects)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if sobre_botao
                                else pygame.SYSTEM_CURSOR_ARROW)


        dica = self.fonte_dica.render("↑ ↓  navegar    ENTER  confirmar    🖱 clique",
                                      True, (60, 25, 25))
        self.tela.blit(dica, (self.largura // 2 - dica.get_width() // 2, self.altura - 35))

        pygame.display.flip()