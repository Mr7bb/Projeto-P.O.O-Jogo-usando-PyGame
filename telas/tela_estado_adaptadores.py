import pygame
from telas.tela_estado_game import EstadoGame
 
class EstadoMenuAdaptador(EstadoGame):
    def handle_event(self, event):
        acao = self.gerenciador.game.tela_inicial.handle_event(event)
        if acao == "JOGAR":
            self.gerenciador.game._resetar_jogo()
            self.gerenciador.mudar_estado("jogo")
        elif acao == "SAIR":
            self.gerenciador.game.rodando = False
 
    def desenhar(self, tela):
        self.gerenciador.game.tela_inicial.draw()
 
 
class EstadoPauseAdaptador(EstadoGame):
    def handle_event(self, event):
        acao = self.gerenciador.game.tela_pause.handle_event(event)
        if acao == "CONTINUAR":
            self.gerenciador.mudar_estado_imediato("jogo")
        elif acao == "MENU PRINCIPAL":
            self.gerenciador.mudar_estado("menu")
        elif acao == "SAIR":
            self.gerenciador.game.rodando = False
 
    def desenhar(self, tela):
        self.gerenciador.game._desenhar_jogo()
        self.gerenciador.game.tela_pause.draw()
 
 
class EstadoGameOverAdaptador(EstadoGame):
    def handle_event(self, event):
        acao = self.gerenciador.game.tela_gameover.handle_event(event)
        if acao == "TENTAR NOVAMENTE":
            self.gerenciador.game._resetar_jogo()
            self.gerenciador.mudar_estado("jogo")
        elif acao == "MENU PRINCIPAL":
            self.gerenciador.mudar_estado("menu")
        elif acao == "SAIR":
            self.gerenciador.game.rodando = False
 
    def desenhar(self, tela):
        self.gerenciador.game.tela_gameover.draw()
 
 
class EstadoLojaAdaptador(EstadoGame):
    def handle_event(self, event):
        self.gerenciador.game.tela_loja.handle_event(event, self.gerenciador.game.inventario, self.gerenciador.game.player)
        # CORREÇÃO: Assim que a loja marcar visivel=False (pelo clique do mouse ou pelo ESC), retorna imediatamente ao jogo normal
        if not self.gerenciador.game.tela_loja.visivel:
            self.gerenciador.mudar_estado_imediato("jogo")
 
    def desenhar(self, tela):
        self.gerenciador.game._desenhar_jogo()
        self.gerenciador.game.tela_loja.draw(self.gerenciador.game.inventario, self.gerenciador.game.player)
