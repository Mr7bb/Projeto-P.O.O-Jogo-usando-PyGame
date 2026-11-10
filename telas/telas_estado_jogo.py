import pygame
from telas.tela_estado_game import EstadoGame
from config import TELA_SIZE
from sons import tocar

class EstadoJogando(EstadoGame):
    def handle_event(self, event):
        g = self.gerenciador.game
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.gerenciador.mudar_estado_imediato("pause")
            elif event.key == pygame.K_e:
                for npc in g.npcs:
                    if npc.perto_do_player(g.player):
                        from telas.tela_estado_dialogo import EstadoDialogo
                        self.gerenciador.estados_registrados["dialogo"] = EstadoDialogo(self.gerenciador, npc)
                        self.gerenciador.mudar_estado_imediato("dialogo")
                        return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                g.player.atacar()
            if event.button == 3:
                if g.player.pode_plantar_bomba() and len(g.bombas) < g.player.max_bombas:
                    col = g.player.rect.centerx // TELA_SIZE
                    lin = g.player.rect.centery // TELA_SIZE
                    from objetos.Bomba import Bomba
                    g.bombas.append(Bomba(col * TELA_SIZE, lin * TELA_SIZE, g.player.nivel_bomba_alcance))
                    g.player.plantar_bomba()
                    tocar('bomba')

    def atualizar(self):
        self.gerenciador.game._processar_frames_jogo()

    def desenhar(self, tela):
        self.gerenciador.game._desenhar_jogo()
