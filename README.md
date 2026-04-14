# Projeto-P.O.O-Jogo-usando-PyGame

Relatório do Jogo: Blast Miner Co.

### 1. Título do Jogo
Blast Miner Co.

### 2. Descrição Geral
Um jogo de Action-Puzzle 2D com visão top-down, inspirado na mecânica clássica de Bomberman. O jogador explora cavernas procedurais ou pré-definidas, utilizando explosivos para abrir caminho através de rochas e enfrentar criaturas subterrâneas em um ambiente retrô pixel-art.

### 3. Objetivo do Jogo
O objetivo principal é descer pelas camadas da terra (fases) até encontrar o Minério Raro no nível mais profundo. Para vencer, o jogador deve gerenciar suas bombas para destruir obstáculos, derrotar o Golem Guardião e sobreviver aos perigos ambientais.

### 4. Personagem Principal
* **Nome:**   Mike (Minerador).
* **Movimentação:** Baseada em grade (Grid-based), movendo-se uma célula por vez.
* **Atributos:**
    * **Vida (HP):** 3 corações.
    * **Velocidade:** Distância percorrida por segundo.
    * **Raio de Explosão:** Tem um raio de 1 quadrado de explosao em forma de cruz, e aumenta a cada upgrade.
    * **Estoque de Bombas:** tem um time pra poder colocar outra bomba, 1 bomba a cada 4 segundos.

### 5. Inimigos e Obstáculos
Fantasmas - eles passivos mas quando eles levam dado eles ficam hostis
golem - Sao mais fortes e causam knockback ao atingir o player
BOSS: golem gigante que spawnam outros mini golens ao perceber o player 

### 6. Cenário (Mapa)
O cenário consiste em uma **matriz (grid)** representando a caverna. 
* **Biomas:** Começa em uma caverna de terra (100m) e transiciona para cavernas de cristal e lava conforme a profundidade aumenta.
* **Itens:** Escondidos atrás de blocos destrutíveis.

### 8. Sistema de Vida
O jogador inicia com **3 vidas**.
* **Dano:** Perde-se 1 vida ao ser tocado por inimigos ou atingido pela própria explosão.
* **Game Over:** Ocorre quando as vidas chegam a zero. Há uma tela de "Contrato Rescindido" oferecendo o restart.

### 9. Controles
| Tecla | Ação |
| :--- | :--- |
| **W, A, S, D** | Movimentação (Cima, Esquerda, Baixo, Direita) |
| **Espaço** | Plantar Bomba |
| **Esc** | Pausar Jogo |

### 10. Fluxo do Jogo
1.  **Menu Principal:** Start, Opções, Sair.
2.  **Gameplay:** O jogador limpa o caminho e busca a escada para o próximo nível.
3.  **Loja Intermediária:** Entre as fases, um NPC vende upgrades.
4.  **Boss Fight:** No último nível, enfrenta o Golem.
5.  **Vitória:** Tela de "Contrato Cumprido" com pontuação final.

### 11. Regras do Jogo
* **Colisão:** O jogador e inimigos não podem atravessar paredes sólidas (Apenas o fantasma pode atravessar).
* **Dano Amigo:** As bombas do jogador podem feri-lo se ele não se afastar do raio de explosão.
* **Temporizador:** A bomba leva 4 segundos para detonar após ser plantada.

### 12. Estrutura do Projeto (POO)
Organização dos arquivos:
* `main.py`: Ponto de entrada e gerenciamento do loop (Pygame).
* `classes.py`: Contém as classes `Player`, `Bomba`, `fantasma`, `golem`, `boss`


### 13. Funcionalidades Mínimas 
* Renderização de um quadrado amarelo (Player) e blocos cinzas (Paredes).
* Movimentação restrita à grade.
* Sistema de colisão funcional (não atravessar blocos).
* Mecânica de colocar uma bomba que remove um bloco após 4 segundos.

### 14. Melhorias Futuras
* Efeitos de partículas para as explosões.
