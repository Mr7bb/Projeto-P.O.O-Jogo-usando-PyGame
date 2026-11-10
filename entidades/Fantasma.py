import pygame
from entidades.Inimigo import Inimigo
from entidades.animacoes import desenhar_animacao
from config import TELA_SIZE
 
class Fantasma(Inimigo):
    """
    fantasma comum: fica patrulhando sozinho, e quando toma dano de bomba entra em furia
    (fica mais rapido e atravessa pedra solta/minerio pra perseguir o player em linha reta).
    so a parede solida (tile 1) para ele de verdade.
    """
 
    COR_NORMAL = (255, 225, 255)   
    COR_FURIA  = (100, 100, 255)   
 
    def __init__(self, x, y):
        # vida 3 -> 6 (ele morria numa picaretada so, agora aguenta 2)
        super().__init__(x=x, y=y, largura=45, altura=45, velocidade=3.5, vida=6, cor=self.COR_NORMAL)
        self.furia_timer = 0
        self.em_movimento = False
        self.sprite_invertido = False
 
    def receber_dano_explosao(self):
        super().receber_dano_explosao() 
        if self.ativo: self._ativar_furia()
 
    def _ativar_furia(self):
        if self.furia_timer <= 0:
            self.furia_timer = 180  
            print(f"[FANTASMA] Entrou em fúria! Vida restante: {self.vida}")
 
    def _colidiu_com_parede_solida(self, mapa):
        # bug corrigido: antes so testava 4 pontinhos nos cantos do retangulo do fantasma,
        # e isso deixava passar situacoes onde uma parede encostava numa borda sem tocar
        # nenhum dos 4 cantos (o fantasma ficava com o corpo meio "dentro" do bloco).
        # agora testa TODOS os tiles que o retangulo do fantasma cobre de verdade.
        col_ini = self.rect.left // TELA_SIZE
        col_fim = (self.rect.right - 1) // TELA_SIZE
        lin_ini = self.rect.top // TELA_SIZE
        lin_fim = (self.rect.bottom - 1) // TELA_SIZE
        for lin in range(lin_ini, lin_fim + 1):
            for col in range(col_ini, col_fim + 1):
                if 0 <= lin < len(mapa) and 0 <= col < len(mapa[0]):
                    if mapa[lin][col] == 1: return True
        return False
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_antiga_x, pos_antiga_y = self.salvar_posicao()
        self.sprite_invertido = player.rect.centerx < self.rect.centerx
 
        if self.furia_timer > 0:
            # furia: vai direto no player, so e barrado por parede solida (tile 1) e bomba
            self.furia_timer -= 1
            self.cor = Fantasma.COR_FURIA
 
            if self.rect.x < player.rect.x: self.mover_x(self.velocidade)
            elif self.rect.x > player.rect.x: self.mover_x(-self.velocidade)
            if mapa and self._colidiu_com_parede_solida(mapa): self.restaurar_x(pos_antiga_x)  
            if bombas:
                for b in bombas:
                    if b.solida and self.rect.colliderect(b.rect): self.restaurar_x(pos_antiga_x)
            
            pos_antiga_y = self._y_preciso
            if self.rect.y < player.rect.y: self.mover_y(self.velocidade)
            elif self.rect.y > player.rect.y: self.mover_y(-self.velocidade)
            if mapa and self._colidiu_com_parede_solida(mapa): self.restaurar_y(pos_antiga_y)  
            if bombas:
                for b in bombas:
                    if b.solida and self.rect.colliderect(b.rect): self.restaurar_y(pos_antiga_y)
        else:
            self.cor = Fantasma.COR_NORMAL
            self._patrulhar_aleatorio(paredes, passos_max=60)

        self.em_movimento = self.rect.topleft != (round(pos_antiga_x), round(pos_antiga_y))

    def desenhar(self, tela, cam_x=0, cam_y=0):
        if self.kb_timer > 0:
            acao = "hurt"
        else:
            acao = "alert" if self.furia_timer > 0 else ("walk" if self.em_movimento else "idle")
        if not desenhar_animacao(
            tela, self, "fantasma", acao, 48, cam_x, cam_y,
            intervalo=8 if acao == "alert" else 12,
            inverter=self.sprite_invertido,
        ):
            super().desenhar(tela, cam_x, cam_y)

class LegiaoDeFantasmas(Fantasma):
    """variante do fantasma que anda em grupo: quando um membro do grupo apanha, todo mundo do grupo entra em furia junto."""
 
    COR_LEGIAO = (180, 100, 255)
    def __init__(self, x, y, grupo):
        super().__init__(x, y)
        # vida 4 -> 7
        self.vida = 7
        self.cor = self.COR_LEGIAO
        self.grupo = grupo  
 
    def receber_dano_explosao(self):
        super().receber_dano_explosao()
        self.alertar_toda_legiao()
 
    def alertar_toda_legiao(self):
        """MECÂNICA PIGMAN CORRIGIDA: Força todos os companheiros vivos do grupo a entrarem em fúria imediata."""
        print(f"[LEGIÃO] Membro atacado! Chamando reforços do além!")
        for membro in self.grupo:
            if membro.ativo: 
                membro._ativar_furia()
