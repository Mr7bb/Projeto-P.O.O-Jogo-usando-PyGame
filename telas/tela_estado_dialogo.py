import pygame
from telas.tela_estado_game import EstadoGame

class EstadoDialogo(EstadoGame):
    def __init__(self, gerenciador, npc):
        super().__init__(gerenciador)
        self.npc = npc
        self.fonte_nome = pygame.font.SysFont("monospace", 22, bold=True)
        self.fonte_texto = pygame.font.SysFont("monospace", 16)
        
        if npc.tipo == "ferreiro":
            self.falas = [
                "Saudações, operador Mike! Vejo que trouxe materiais.",
                "Consigo aprimorar sua picareta e o raio de suas bombas.",
                "O trabalho aqui é duro, mas justo. Vamos negociar? [ESPAÇO]"
            ]
        else:
            self.falas = [
                "Shhh... escute os ecos destas paredes místicas...",
                "Troco essas Essências Fantasmais e Gosmas por pura vitalidade.",
                "Não tema os esporos venenosos, eu tenho a cura. Veja... [ESPAÇO]"
            ]
        self.indice = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.indice += 1
                if self.indice >= len(self.falas):
                    # Abre a loja correspondente na interface e muda o estado
                    self.gerenciador.game.tela_loja.abrir(self.npc.tipo)
                    self.gerenciador.mudar_estado_imediato("loja")
            elif event.key == pygame.K_ESCAPE:
                # CORREÇÃO: Permite cancelar a conversa e voltar ao jogo normal
                self.gerenciador.mudar_estado_imediato("jogo")

    def desenhar(self, tela):
        # Renderiza o cenário de jogo estático como fundo do diálogo
        self.gerenciador.estados_registrados["jogo"].desenhar(tela)
        
        # Caixa do Diálogo
        larg, alt = 850, 150
        x = (tela.get_width() - larg) // 2
        y = tela.get_height() - alt - 60
        
        pygame.draw.rect(tela, (15, 15, 25), (x, y, larg, alt), border_radius=8)
        pygame.draw.rect(tela, self.npc.cor, (x, y, larg, alt), 3, border_radius=8)
        
        # Nome do NPC
        txt_nome = self.fonte_nome.render(f"◆ {self.npc.nome} ◆", True, self.npc.cor)
        tela.blit(txt_nome, (x + 25, y + 15))
        
        # Linha Divisória
        pygame.draw.line(tela, (50, 50, 70), (x + 25, y + 45), (x + larg - 25, y + 45), 1)
        
        # Texto da Fala
        txt_fala = self.fonte_texto.render(self.falas[self.indice], True, (230, 230, 250))
        tela.blit(txt_fala, (x + 25, y + 65))
        
        # Dica de comando
        txt_dica = self.fonte_texto.render("[ESPAÇO] Avançar    [ESC] Sair", True, (100, 100, 120))
        tela.blit(txt_dica, (x + larg - txt_dica.get_width() - 25, y + alt - 28))