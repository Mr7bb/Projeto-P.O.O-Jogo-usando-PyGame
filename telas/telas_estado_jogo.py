import pygame
from telas.tela_estado_game import EstadoGame

class EstadoJogando(EstadoGame):
    def handle_event(self, event):
        g = self.gerenciador.game
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.gerenciador.mudar_estado_imediato("pause")
            elif event.key == pygame.K_e:
                # Verifica se há NPCs próximos para abrir diálogo por máquina de estados
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
                    col = g.player.rect.centerx // 50
                    lin = g.player.rect.centery // 50
                    from objetos.Bomba import Bomba
                    g.bombas.append(Bomba(col * 50, lin * 50, g.player.nivel_bomba_alcance))
                    g.player.plantar_bomba()

    def atualizar(self):
        self.gerenciador.game._processar_frames_jogo()

    def desenhar(self, tela):
        self.gerenciador.game._desenhar_jogo()