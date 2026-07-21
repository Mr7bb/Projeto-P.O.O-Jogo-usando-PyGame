import pygame
import random
from entidades.Inimigo import Inimigo
from config import TELA_SIZE
 
 
class AtaqueAreaTelegrafado:
 
    def __init__(self, rect, tempo_aviso, dano, cor=(255, 90, 40)):
        self.rect = rect
        self.timer = tempo_aviso
        self.tempo_aviso = tempo_aviso
        self.dano = dano
        self.cor = cor
        self.detonou = False
        self.ativo = True
 
    def atualizar(self, player):
        if self.detonou:
            self.ativo = False
            return
        self.timer -= 1
        if self.timer <= 0:
            self.detonou = True
            if self.rect.colliderect(player.rect):
                player.receber_dano(self.dano)
 
    def desenhar(self, tela, cam_x=0, cam_y=0):
        if self.detonou: return
        r = pygame.Rect(self.rect.x - cam_x, self.rect.y - cam_y, self.rect.width, self.rect.height)
        pisca = (self.timer // 6) % 2 == 0
        cor = self.cor if pisca else (255, 230, 90)
        surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        surf.fill((*cor, 90))
        tela.blit(surf, (r.x, r.y))
        pygame.draw.rect(tela, cor, r, 2)
 
 
class Boss(Inimigo):
    """
    classe mae de todo boss de fase. cada boss guarda o nome pra HUD, a vida maxima
    (pra barra de vida e pra calcular a marca de 50%) e a lista de ataques em area
    telegrafados que estao pendentes/tocando no momento.
    """
 
    NOME_EXIBICAO = "Boss"
 
    def __init__(self, x, y, largura, altura, velocidade, vida, cor):
        super().__init__(x, y, largura, altura, velocidade, vida, cor)
        self.vida_max = vida
        self.ataques_ativos = []
 
    def atualizar_ataques(self, player, paredes=None, mapa=None):
        """chamado todo frame pelo Blast_Miner.py pra cada boss vivo. cada boss
        sobrescreve isso pra decidir QUANDO disparar um golpe novo, mas sempre chama
        super() primeiro pra manter os ataques telegrafados em andamento."""
        for atk in self.ataques_ativos[:]:
            atk.atualizar(player)
            if not atk.ativo:
                self.ataques_ativos.remove(atk)
 
    def desenhar_ataques(self, tela, cam_x=0, cam_y=0):
        for atk in self.ataques_ativos:
            atk.desenhar(tela, cam_x, cam_y)
 
    def desenhar_extra(self, tela, cam_x=0, cam_y=0):
        """gancho pra efeitos visuais extras que nao sao ataques telegrafados
        (por exemplo as pocas de lodo do Gruk). cada boss sobrescreve se precisar."""
        pass
 
 

class EcoPerdido(Boss):
    """
    alterna entre Forma Fantasma (intangivel, atravessa parede, IMUNE a dano) e
    Forma Material (vulneravel, mais lenta). a bomba nao causa dano na forma
    fantasma, mas forca a transicao imediata pra forma material -- essa e a
    "janela de dano" que o documento pede.
    """
 
    NOME_EXIBICAO = "O Eco Perdido"
    COR_FANTASMA = (200, 200, 255)
    COR_MATERIAL = (120, 90, 160)
 
    DURACAO_FANTASMA = 240   # 4s andando intangivel antes de virar material sozinho
    DURACAO_MATERIAL = 180   # 3s vulneravel antes de voltar a ser fantasma
 
    def __init__(self, x, y):
        super().__init__(x, y, largura=52, altura=52, velocidade=2.2, vida=40, cor=self.COR_FANTASMA)
        self.forma = "fantasma"
        self.timer_forma = self.DURACAO_FANTASMA
        self.cooldown_sussurro = 150
        self.cooldown_picareta_fantasma = 220
        self.invocou_metade = False
        self.invocacoes_pendentes = []
        self.projeteis_pendentes = []
 
    def _forcar_material(self):
        if self.forma == "fantasma":
            self.forma = "material"
            self.timer_forma = self.DURACAO_MATERIAL
            self.cor = self.COR_MATERIAL
 
    def receber_dano_explosao(self, dano=2):
        if self.forma == "fantasma":
            # regra de ouro do documento: a bomba serve pra ABRIR a vulnerabilidade,
            # nao pra bater direto (nao causa dano aqui, so forca a transicao)
            self._forcar_material()
        else:
            super().receber_dano_explosao(dano)
            self._checar_invocacao()
 
    def receber_dano_picareta(self, dano, player_rect):
        if self.forma == "fantasma":
            return  # picareta nao atravessa a forma intangivel
        super().receber_dano_picareta(dano, player_rect)
        self._checar_invocacao()
 
    def _checar_invocacao(self):
        # Invocacao dos Perdidos: ao atingir 50% de HP, chama 2 fantasmas comuns
        if not self.invocou_metade and self.ativo and self.vida <= self.vida_max // 2:
            self.invocou_metade = True
            self.invocacoes_pendentes.append((self.rect.centerx - 60, self.rect.centery))
            self.invocacoes_pendentes.append((self.rect.centerx + 60, self.rect.centery))
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_x, pos_y = self.rect.x, self.rect.y
 
        self.timer_forma -= 1
        if self.timer_forma <= 0:
            if self.forma == "fantasma":
                self._forcar_material()
            else:
                self.forma = "fantasma"
                self.timer_forma = self.DURACAO_FANTASMA
                self.cor = self.COR_FANTASMA
 
        if self.rect.x < player.rect.x: self.rect.x += self.velocidade
        elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade
        if self.rect.y < player.rect.y: self.rect.y += self.velocidade
        elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade
 
        if self.forma == "material":
            # so na forma material que ele esbarra em parede de verdade
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x, self.rect.y = pos_x, pos_y
                    break
 
        if self.cooldown_sussurro > 0: self.cooldown_sussurro -= 1
        if self.cooldown_picareta_fantasma > 0: self.cooldown_picareta_fantasma -= 1
 
    def atualizar_ataques(self, player, paredes=None, mapa=None):
        super().atualizar_ataques(player, paredes, mapa)
 
        # Sussurro da Mina: marca blocos perto do player, exploram 2s depois
        if self.cooldown_sussurro <= 0 and self.ativo:
            self.cooldown_sussurro = 220
            for _ in range(3):
                ox = random.randint(-3, 3) * TELA_SIZE
                oy = random.randint(-3, 3) * TELA_SIZE
                area = pygame.Rect(player.rect.centerx + ox - 25, player.rect.centery + oy - 25, 50, 50)
                self.ataques_ativos.append(AtaqueAreaTelegrafado(area, tempo_aviso=120, dano=16, cor=(180, 120, 255)))
 
        # Picareta Fantasma: projetil espectral que atravessa parede
        if self.cooldown_picareta_fantasma <= 0 and self.ativo:
            self.cooldown_picareta_fantasma = 240
            self.projeteis_pendentes.append((self.rect.centerx, self.rect.centery, player.rect.centerx, player.rect.centery))
 
    def desenhar(self, tela):
        if self.forma == "fantasma":
            surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            surf.fill((*self.COR_FANTASMA, 140))
            tela.blit(surf, (self.rect.x, self.rect.y))
            pygame.draw.rect(tela, self.COR_FANTASMA, self.rect, 2)
        else:
            pygame.draw.rect(tela, self.COR_MATERIAL, self.rect)
            pygame.draw.rect(tela, (40, 20, 60), self.rect, 3)
 
 

class Gruk(Boss):
    """
    hibrido goblin/slime. o golpe principal e a Investida: se ele bater numa parede
    no meio da investida, fica atordoado (o "nucleo de slime exposto nas costas" do
    documento) e leva o dobro de dano da picareta enquanto isso.
    """
 
    NOME_EXIBICAO = "Gruk, o Senhor da Mina Verde"
    COR_NORMAL = (70, 150, 60)
    COR_INVESTIDA = (200, 60, 40)
    COR_ATORDOADO = (255, 220, 80)
 
    def __init__(self, x, y):
        super().__init__(x, y, largura=56, altura=56, velocidade=2, vida=55, cor=self.COR_NORMAL)
        self.cooldown_pancada = 170
        self.cooldown_investida = 260
        self.cooldown_lodo = 200
        self.investindo = False
        self._timer_investida = 0
        self.investida_dx = self.investida_dy = 0
        self.atordoado_timer = 0
        self.invocou_metade = False
        self.invocacoes_pendentes = []
        self.pocas_lodo = []  # cada item: {"rect": Rect, "timer": int}
 
    def receber_dano_picareta(self, dano, player_rect):
        if self.atordoado_timer > 0:
            dano *= 2  # nucleo exposto: dano critico (regra do documento)
        super().receber_dano_picareta(dano, player_rect)
        self._checar_invocacao()
 
    def receber_dano_explosao(self, dano=2):
        super().receber_dano_explosao(dano)
        self._checar_invocacao()
 
    def _checar_invocacao(self):
        # Invocar Slimes: com 50% de HP, expele 3 slimes pequenos
        if not self.invocou_metade and self.ativo and self.vida <= self.vida_max // 2:
            self.invocou_metade = True
            for dx in (-50, 0, 50):
                self.invocacoes_pendentes.append((self.rect.centerx + dx, self.rect.centery + 50))
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_x, pos_y = self.rect.x, self.rect.y
 
        if self.atordoado_timer > 0:
            self.atordoado_timer -= 1
            self.cor = self.COR_ATORDOADO
            return
 
        if self.investindo:
            self.rect.x += self.investida_dx
            self.rect.y += self.investida_dy
            self._timer_investida -= 1
            bateu = False
            for p in paredes:
                if self.rect.colliderect(p):
                    self.rect.x, self.rect.y = pos_x, pos_y
                    bateu = True
                    break
            if bateu or self._timer_investida <= 0:
                self.investindo = False
                if bateu:
                    # bateu contra uma parede solida: fica atordoado 3s (documento)
                    self.atordoado_timer = 180
                    self.cor = self.COR_ATORDOADO
                else:
                    self.cor = self.COR_NORMAL
            return
 
        if self.rect.x < player.rect.x: self.rect.x += self.velocidade
        elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade
        if self.rect.y < player.rect.y: self.rect.y += self.velocidade
        elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x, self.rect.y = pos_x, pos_y
                break
 
        if self.cooldown_pancada > 0: self.cooldown_pancada -= 1
        if self.cooldown_investida > 0: self.cooldown_investida -= 1
        if self.cooldown_lodo > 0: self.cooldown_lodo -= 1
 
        for poca in self.pocas_lodo[:]:
            poca["timer"] -= 1
            if poca["timer"] <= 0:
                self.pocas_lodo.remove(poca)
 
    def atualizar_ataques(self, player, paredes=None, mapa=None):
        super().atualizar_ataques(player, paredes, mapa)
        if self.atordoado_timer > 0 or self.investindo:
            return
 
        dist = ((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2) ** 0.5
 
        if self.cooldown_pancada <= 0:
            # Pancada Sismica: onda de choque radial ao redor do proprio Gruk
            self.cooldown_pancada = 230
            area = pygame.Rect(self.rect.centerx - 110, self.rect.centery - 110, 220, 220)
            self.ataques_ativos.append(AtaqueAreaTelegrafado(area, tempo_aviso=50, dano=20, cor=(255, 150, 60)))
 
        elif self.cooldown_investida <= 0 and 60 < dist < 420:
            # Investida Goblin: corrida reta na direcao do player
            self.cooldown_investida = 270
            self.investindo = True
            self._timer_investida = 30
            self.cor = self.COR_INVESTIDA
            mag = max(dist, 1)
            self.investida_dx = (player.rect.centerx - self.rect.centerx) / mag * 11
            self.investida_dy = (player.rect.centery - self.rect.centery) / mag * 11
 
        if self.cooldown_lodo <= 0:
            # Lodo Corrosivo: poca no chao que reduz a velocidade do player em 40%
            self.cooldown_lodo = 320
            for _ in range(2):
                px = self.rect.centerx + random.randint(-160, 160)
                py = self.rect.centery + random.randint(-160, 160)
                self.pocas_lodo.append({"rect": pygame.Rect(px - 30, py - 30, 60, 60), "timer": 300})
 
    def desenhar_extra(self, tela, cam_x=0, cam_y=0):
        for poca in self.pocas_lodo:
            r = poca["rect"]
            rr = pygame.Rect(r.x - cam_x, r.y - cam_y, r.width, r.height)
            surf = pygame.Surface((rr.width, rr.height), pygame.SRCALPHA)
            surf.fill((60, 160, 40, 120))
            tela.blit(surf, (rr.x, rr.y))
 
    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
        # dois olhos, pra lembrar que ele veio do goblin
        pygame.draw.circle(tela, (255, 240, 60), (self.rect.centerx - 10, self.rect.centery - 8), 4)
        pygame.draw.circle(tela, (255, 240, 60), (self.rect.centerx + 10, self.rect.centery - 8), 4)
 
 
class Mykros(Boss):
    """
    boss de controle de zona. invoca Cogumelos Parasitas (reaproveita a classe
    CogumeloEsporos ja existente, que ja atira esporo -- economiza reimplementar
    a mesma logica de ataque a distancia). enquanto tiver parasita vivo, regenera
    HP aos poucos; a bomba limpa varios parasitas de uma vez e corta a regeneracao.
    """
 
    NOME_EXIBICAO = "Mykros, o Coracao da Colonia"
    COR = (90, 60, 130)
 
    def __init__(self, x, y):
        super().__init__(x, y, largura=60, altura=60, velocidade=0.6, vida=70, cor=self.COR)
        self.cooldown_esporos = 160
        self.cooldown_parasitas = 260
        self.parasitas_vivos = []
        self.invocacoes_pendentes = []
        self.timer_parado_player = 0
        self._ultima_pos_player = None
        self._regen_tick = 0
 
    def receber_dano_explosao(self, dano=2):
        # Fraqueza do documento: a bomba limpa os parasitas de uma vez e cancela a
        # regeneracao da colonia
        for p in self.parasitas_vivos:
            if p.ativo:
                p.ativo = False
        super().receber_dano_explosao(dano)
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_x, pos_y = self.rect.x, self.rect.y
 
        if self.rect.x < player.rect.x: self.rect.x += self.velocidade
        elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade
        if self.rect.y < player.rect.y: self.rect.y += self.velocidade
        elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x, self.rect.y = pos_x, pos_y
                break
 
        if self.cooldown_esporos > 0: self.cooldown_esporos -= 1
        if self.cooldown_parasitas > 0: self.cooldown_parasitas -= 1
 
        # Raizes Perseguidoras: conta quanto tempo o player fica parado no lugar
        if self._ultima_pos_player == player.rect.topleft:
            self.timer_parado_player += 1
        else:
            self.timer_parado_player = 0
        self._ultima_pos_player = player.rect.topleft
 
    def atualizar_ataques(self, player, paredes=None, mapa=None):
        super().atualizar_ataques(player, paredes, mapa)
        self.parasitas_vivos = [p for p in self.parasitas_vivos if p.ativo]
 
        # Chuva de Esporos: retriculos vermelhos aleatorios perto do boss
        if self.cooldown_esporos <= 0 and self.ativo:
            self.cooldown_esporos = 220
            for _ in range(3):
                ox = random.randint(-4, 4) * TELA_SIZE
                oy = random.randint(-4, 4) * TELA_SIZE
                area = pygame.Rect(self.rect.centerx + ox - 25, self.rect.centery + oy - 25, 50, 50)
                self.ataques_ativos.append(AtaqueAreaTelegrafado(area, tempo_aviso=70, dano=14, cor=(180, 60, 200)))
 
        # Raizes Perseguidoras: se o player ficar 1.5s parado, uma raiz nasce nos pes dele
        if self.timer_parado_player >= 90:
            self.timer_parado_player = 0
            area = pygame.Rect(player.rect.centerx - 25, player.rect.centery - 25, 50, 50)
            self.ataques_ativos.append(AtaqueAreaTelegrafado(area, tempo_aviso=25, dano=16, cor=(120, 200, 80)))
 
        # Cogumelos Parasitas: invoca ate 4 de uma vez, so reinvoca se ja mataram os antigos
        if self.cooldown_parasitas <= 0 and self.ativo and len(self.parasitas_vivos) < 4:
            self.cooldown_parasitas = 340
            for dx, dy in [(-140, -140), (140, -140), (-140, 140), (140, 140)]:
                self.invocacoes_pendentes.append((self.rect.centerx + dx, self.rect.centery + dy))
 
        # Cura da Colonia: regenera 1% do HP maximo por segundo enquanto tiver parasita vivo
        self._regen_tick += 1
        if self._regen_tick >= 60:
            self._regen_tick = 0
            if self.parasitas_vivos and self.ativo:
                self.vida = min(self.vida_max, self.vida + max(1, self.vida_max // 100))
 
    def desenhar(self, tela):
        pygame.draw.ellipse(tela, self.cor, self.rect)
        chapeu = pygame.Rect(self.rect.x - 10, self.rect.y - 14, self.rect.width + 20, 20)
        pygame.draw.ellipse(tela, (170, 90, 190), chapeu)
 

class Guardiao(Boss):
    """
    a picareta causa 0 de dano enquanto a Armadura de Pedra estiver ativa -- a bomba
    e OBRIGATORIA pra quebrar a carcaca e expor o nucleo (janela de dano com bonus,
    igual descreve o documento).
    """
 
    NOME_EXIBICAO = "O Guardiao"
    COR_ARMADURA = (110, 120, 130)
    COR_EXPOSTO = (80, 220, 255)
 
    DURACAO_EXPOSTO = 150  # 2.5s de janela de dano depois que a bomba quebra a armadura
 
    def __init__(self, x, y):
        super().__init__(x, y, largura=62, altura=62, velocidade=1, vida=90, cor=self.COR_ARMADURA)
        self.armadura_ativa = True
        self.timer_exposto = 0
        self.cooldown_soco = 170
        self.cooldown_chuva = 260
        self.cooldown_prisao = 360
 
    def receber_dano_picareta(self, dano, player_rect):
        if self.armadura_ativa:
            print("[GUARDIAO] A espada nao passa da Armadura de Pedra!")
            return  # 0 de dano enquanto blindado (regra do documento)
        super().receber_dano_picareta(dano, player_rect)
 
    def receber_dano_explosao(self, dano=2):
        if self.armadura_ativa:
            self.armadura_ativa = False
            self.timer_exposto = self.DURACAO_EXPOSTO
            self.cor = self.COR_EXPOSTO
            print("[GUARDIAO] Armadura quebrada! Nucleo exposto.")
        else:
            super().receber_dano_explosao(dano * 2)  # nucleo exposto: dano critico
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_x, pos_y = self.rect.x, self.rect.y
 
        if not self.armadura_ativa:
            self.timer_exposto -= 1
            if self.timer_exposto <= 0:
                self.armadura_ativa = True
                self.cor = self.COR_ARMADURA
 
        if self.rect.x < player.rect.x: self.rect.x += self.velocidade
        elif self.rect.x > player.rect.x: self.rect.x -= self.velocidade
        if self.rect.y < player.rect.y: self.rect.y += self.velocidade
        elif self.rect.y > player.rect.y: self.rect.y -= self.velocidade
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x, self.rect.y = pos_x, pos_y
                break
 
        if self.cooldown_soco > 0: self.cooldown_soco -= 1
        if self.cooldown_chuva > 0: self.cooldown_chuva -= 1
        if self.cooldown_prisao > 0: self.cooldown_prisao -= 1
 
    def atualizar_ataques(self, player, paredes=None, mapa=None):
        super().atualizar_ataques(player, paredes, mapa)
 
        if self.cooldown_soco <= 0:
            # Soco Sismico / Rachadura: fenda em linha reta na direcao do player
            self.cooldown_soco = 220
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            passos = 6
            for i in range(1, passos + 1):
                px = self.rect.centerx + dx * (i / passos)
                py = self.rect.centery + dy * (i / passos)
                area = pygame.Rect(px - 25, py - 25, 50, 50)
                self.ataques_ativos.append(AtaqueAreaTelegrafado(area, tempo_aviso=45, dano=20, cor=(90, 180, 255)))
 
        elif self.cooldown_chuva <= 0:
            # Chuva de Rochas: blocos caindo em posicoes aleatorias perto do player
            self.cooldown_chuva = 260
            for _ in range(4):
                ox = random.randint(-5, 5) * TELA_SIZE
                oy = random.randint(-5, 5) * TELA_SIZE
                area = pygame.Rect(player.rect.centerx + ox - 25, player.rect.centery + oy - 25, 50, 50)
                self.ataques_ativos.append(AtaqueAreaTelegrafado(area, tempo_aviso=80, dano=18, cor=(140, 220, 255)))
 
        elif self.cooldown_prisao <= 0:
            # Prisao de Cristal: 4 pontos de dano cercando o player (versao simplificada
            # da prisao solida do documento -- aqui e area de dano, nao bloco fisico)
            self.cooldown_prisao = 400
            cx, cy = player.rect.centerx, player.rect.centery
            for dx, dy in [(-70, 0), (70, 0), (0, -70), (0, 70)]:
                area = pygame.Rect(cx + dx - 25, cy + dy - 25, 50, 50)
                self.ataques_ativos.append(AtaqueAreaTelegrafado(area, tempo_aviso=60, dano=10, cor=(150, 150, 255)))
 
    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
        borda = (255, 255, 255) if not self.armadura_ativa else (60, 60, 70)
        pygame.draw.rect(tela, borda, self.rect, 3)
 

class CoracaoDaMina(Boss):
    """
    chefe final, 3 fases (troca de fase por porcentagem de HP, igual a tabela do
    documento). fase 2 reusa a ideia de esporo/fenda dos bosses anteriores, fase 3
    liga um "laser" central periodico e dobra o dano da bomba no nucleo exposto.
    """
 
    NOME_EXIBICAO = "O Coracao da Mina"
    COR_FASE1 = (200, 90, 40)
    COR_FASE2 = (140, 60, 160)
    COR_FASE3 = (255, 60, 30)
 
    def __init__(self, x, y):
        super().__init__(x, y, largura=64, altura=64, velocidade=1.4, vida=140, cor=self.COR_FASE1)
        self.fase_luta = 1
        self.cooldown_ataque = 140
        self.cooldown_especial = 260
        self.preso_timer = 0
        self._laser_timer = 300
        self.invocacoes_pendentes = []
 
    def _atualizar_fase_luta(self):
        if not self.ativo: return
        pct = self.vida / self.vida_max
        if pct <= 1 / 3 and self.fase_luta < 3:
            self.fase_luta = 3
            self.cor = self.COR_FASE3
            print("[CORACAO DA MINA] Fase 3: Colapso Vulcanico!")
        elif pct <= 2 / 3 and self.fase_luta < 2:
            self.fase_luta = 2
            self.cor = self.COR_FASE2
            print("[CORACAO DA MINA] Fase 2: Mina Viva!")
 
    def receber_dano_picareta(self, dano, player_rect):
        if self.preso_timer > 0:
            dano *= 2  # preso no chao apos errar o golpe pesado: janela critica
        super().receber_dano_picareta(dano, player_rect)
        self._atualizar_fase_luta()
 
    def receber_dano_explosao(self, dano=2):
        if self.fase_luta >= 3:
            dano *= 2  # nucleo exposto na lava (fase 3): dano em dobro na bomba
        super().receber_dano_explosao(dano)
        self._atualizar_fase_luta()
 
    def mover(self, player, paredes, mapa=None, bombas=None):
        if self._aplicar_knockback_proprio(paredes): return
        pos_x, pos_y = self.rect.x, self.rect.y
 
        if self.preso_timer > 0:
            self.preso_timer -= 1
            return
 
        vel = self.velocidade * (1.3 if self.fase_luta >= 2 else 1.0)
        if self.rect.x < player.rect.x: self.rect.x += vel
        elif self.rect.x > player.rect.x: self.rect.x -= vel
        if self.rect.y < player.rect.y: self.rect.y += vel
        elif self.rect.y > player.rect.y: self.rect.y -= vel
        for p in paredes:
            if self.rect.colliderect(p):
                self.rect.x, self.rect.y = pos_x, pos_y
                break
 
        if self.cooldown_ataque > 0: self.cooldown_ataque -= 1
        if self.cooldown_especial > 0: self.cooldown_especial -= 1
 
    def atualizar_ataques(self, player, paredes=None, mapa=None):
        super().atualizar_ataques(player, paredes, mapa)
        if self.preso_timer > 0 or not self.ativo:
            return
 
        # Fase 1: picareta em brasa. se o player estiver longe, o golpe erra e ele
        # fica preso no chao por um tempo (janela de dano critico)
        if self.cooldown_ataque <= 0:
            self.cooldown_ataque = 130
            dist = ((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2) ** 0.5
            area = pygame.Rect(player.rect.centerx - 30, player.rect.centery - 30, 60, 60)
            self.ataques_ativos.append(AtaqueAreaTelegrafado(area, tempo_aviso=40, dano=24, cor=(255, 120, 40)))
            if dist > 130:
                self.preso_timer = 90
 
        # Fase 2: Mina Viva -- reusa a mecanica de nuvem toxica/fenda dos bosses anteriores
        if self.fase_luta >= 2 and self.cooldown_especial <= 0:
            self.cooldown_especial = 240
            for _ in range(3):
                ox = random.randint(-4, 4) * TELA_SIZE
                oy = random.randint(-4, 4) * TELA_SIZE
                area = pygame.Rect(player.rect.centerx + ox - 25, player.rect.centery + oy - 25, 50, 50)
                self.ataques_ativos.append(AtaqueAreaTelegrafado(area, tempo_aviso=65, dano=16, cor=(200, 90, 220)))
 
        # Fase 3: Colapso Vulcanico -- raio central periodico
        if self.fase_luta >= 3:
            self._laser_timer -= 1
            if self._laser_timer <= 0:
                self._laser_timer = 280
                area = pygame.Rect(self.rect.centerx - 30, self.rect.centery - 300, 60, 600)
                self.ataques_ativos.append(AtaqueAreaTelegrafado(area, tempo_aviso=55, dano=28, cor=(255, 200, 60)))
 
    def desenhar(self, tela):
        pygame.draw.rect(tela, self.cor, self.rect)
        borda = (255, 220, 100) if self.preso_timer > 0 else (30, 10, 5)
        pygame.draw.rect(tela, borda, self.rect, 3)