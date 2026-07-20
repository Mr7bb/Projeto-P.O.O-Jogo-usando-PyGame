import pygame
 
 
class TelaPause:
    def __init__(self, tela):
        self.tela    = tela
        self.largura = tela.get_width()
        self.altura  = tela.get_height()
 
        self.fonte_titulo = pygame.font.SysFont("monospace", 52, bold=True)
        self.fonte_menu   = pygame.font.SysFont("monospace", 32, bold=True)
        self.fonte_dica   = pygame.font.SysFont("monospace", 16)
 
        self.opcoes      = ["CONTINUAR", "MENU PRINCIPAL", "SAIR"]
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
        # ── overlay escuro sobre o jogo ────────────────────────────────────
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.tela.blit(overlay, (0, 0))
 
        # ── caixa central ─────────────────────────────────────────────────
        box_w, box_h = 380, 320
        box_x = self.largura // 2 - box_w // 2
        box_y = self.altura  // 2 - box_h // 2
        pygame.draw.rect(self.tela, (18, 18, 25),
                         (box_x, box_y, box_w, box_h), border_radius=10)
        pygame.draw.rect(self.tela, (255, 200, 0),
                         (box_x, box_y, box_w, box_h), 2, border_radius=10)
 
        # ── título ────────────────────────────────────────────────────────
        titulo = self.fonte_titulo.render("⏸ PAUSE", True, (255, 200, 0))
        self.tela.blit(titulo, (self.largura // 2 - titulo.get_width() // 2, box_y + 20))
 
        # separador
        pygame.draw.line(self.tela, (60, 60, 80),
                         (box_x + 20, box_y + 85), (box_x + box_w - 20, box_y + 85), 1)
 
        # ── botões ────────────────────────────────────────────────────────
        self.botao_rects = []
        btn_w = 280
        btn_x = self.largura // 2 - btn_w // 2
        mx, my = pygame.mouse.get_pos()
 
        for i, opcao in enumerate(self.opcoes):
            y_pos = box_y + 110 + i * 65
            rect  = pygame.Rect(btn_x, y_pos, btn_w, 48)
            self.botao_rects.append(rect)
 
            hover      = rect.collidepoint(mx, my)
            ativo      = i == self.selecionado or hover
 
            if ativo:
                pygame.draw.rect(self.tela, (40, 38, 10), rect, border_radius=6)
                pygame.draw.rect(self.tela, (255, 200, 0), rect, 2, border_radius=6)
                cor     = (255, 200, 0)
                prefixo = "> "
            else:
                cor     = (130, 130, 150)
                prefixo = "  "
 
            texto = self.fonte_menu.render(prefixo + opcao, True, cor)
            self.tela.blit(texto, (self.largura // 2 - texto.get_width() // 2, y_pos + 8))
 
        # cursor
        sobre_botao = any(r.collidepoint(mx, my) for r in self.botao_rects)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if sobre_botao
                                else pygame.SYSTEM_CURSOR_ARROW)
 
        # dica
        dica = self.fonte_dica.render("ESC  retomar    ↑ ↓  navegar    ENTER  confirmar",
                                      True, (55, 55, 70))
        self.tela.blit(dica, (self.largura // 2 - dica.get_width() // 2,
                               box_y + box_h - 25))
 
        pygame.display.flip()
