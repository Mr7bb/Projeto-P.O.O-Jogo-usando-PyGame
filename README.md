# Blast Miner Co.

## 📝 Relatório do Jogo e GDD (Game Design Document)

### 1. Título do Jogo
**Blast Miner Co.** (Edição Roguelite RPG)

### 2. Descrição Geral
Blast Miner Co. é um jogo de **RPG de Ação e Exploração 2D** com visão top-down, desenvolvido em Python utilizando a biblioteca Pygame. Inspirado na atmosfera de exploração orgânica de *Stardew Valley* e nas dinâmicas de combate, salas procedurais e sinergia de itens de *The Binding of Isaac*, o jogo coloca o jogador no papel de um minerador preso em profundezas perigosas e em constante transformação.

### 3. Objetivo do Jogo
O objetivo principal é explorar **13 fases** subterrâneas geradas proceduralmente, coletando recursos, enfrentando criaturas e comprando melhorias. A jornada termina na fase 13, no Núcleo Vulcânico, onde o jogador enfrenta **O Coração da Mina**. Depois de limpar a arena, basta entrar na saída para concluir a jornada e retornar ao menu principal.

---

### 4. Personagem Principal (Mike)
O protagonista é **Mike**, um minerador dedicado e azarado da Blast Miner Co. 
* **Movimentação:** Livre e contínua pelo cenário (abandonando a movimentação rígida presa a blocos).
* **Atributos Iniciais:**
  * **Vida (HP):** Começa em 2000 pontos e é exibida em uma barra na interface.
  * **Força e Alcance:** Melhorias compradas na loja aumentam o dano da picareta e o raio das bombas.
  * **Velocidade de Movimento:** Medida em pixels por frame; pode ser aprimorada na loja.
  * **Capacidade de Explosivos:** Começa com uma bomba simultânea. O upgrade do Ferreiro libera a segunda.
* **Direcionamento:** O personagem monitora constantemente para qual dos 4 eixos (Cima, Baixo, Esquerda, Direita) está olhando, influenciando a direção de seus ataques.

---

### 5. Inimigos e Obstáculos
O jogo conta com um ecossistema de criaturas com comportamentos distintos e ataques telegrafados (sinais visuais antes de agir):
* **Fantasmas:** Patrulham a caverna. Quando entram em fúria, perseguem o jogador e atravessam obstáculos destrutíveis, mas continuam bloqueados por paredes sólidas.
* **Cogumelos:** O Cogumelo de Esporos fica parado e dispara projéteis venenosos; o Cogumelo Agressivo persegue o jogador e pode realizar uma investida.
* **Golems de Pedra:** Monstros robustos e lentos que perseguem o jogador quando ele entra no raio de detecção. Ao encostar, causam dano e podem aplicar *knockback* (empurrão) com intervalo entre os golpes.
* **Chefes de bioma:** O Eco Perdido (fase 3), Gruk (fase 6), Mykros (fase 9), O Guardião (fase 12) e O Coração da Mina (fase 13). O Golem de Lava aparece como inimigo comum nas fases 10 e 11.

---

### 6. Cenário e Geração Procedural Orgânica
O mapa do jogo abandona os labirintos simétricos e geométricos para criar **cavernas de formato natural**.

* **Algoritmo de Autômatos Celulares:** As paredes rochosas permanentes são geradas simulando processos de erosão natural, criando curvas, salões amplos e reentrâncias.
* **Detritos Soltos:** O chão das salas é livre e aberto. Obstáculos destrutíveis como **Pedras Comuns** e **Veios de Minério Raro** são distribuídos de forma espalhada pelo chão, funcionando como objetos individuais.
* **A Mecânica da Saída:** Cada mapa possui uma saída bloqueada. Depois que todos os inimigos da fase são derrotados, a saída é liberada; entrar nela leva à fase seguinte. Na fase 13, a saída encerra a campanha e mostra a tela de parabéns.
* **Sistema de Spawn Seguro:** Ao descer para uma nova caverna, o Mike cai em uma coordenada de solo limpo totalmente aleatória. Para garantir a justiça do gameplay, os monstros só podem surgir em áreas localizadas fora de um **raio de segurança de 5 blocos** de distância do jogador.

#### 🎨 Progressão de Biomas
O motor visual do jogo lê a profundidade atual e altera dinamicamente a paleta de cores dos blocos:
1. **Bioma 1: Caverna Normal (Fases 1-3):** Paleta cinza-azulada; apresenta fantasmas e termina com O Eco Perdido.
2. **Bioma 2: Cavernas dos Goblins (Fases 4-6):** Paleta escura e esverdeada, com goblins, slimes e o chefe Gruk.
3. **Bioma 3: Cavernas de Fungos (Fases 7-9):** Região esverdeada com cogumelos, esporos e o chefe Mykros.
4. **Bioma 4: Minas de Cristal (Fases 10-12):** Região azulada com golems e o chefe Guardião.
5. **Bioma 5: Núcleo Vulcânico (Fase 13):** Região avermelhada e final da jornada, com O Coração da Mina.

---

### 7. Sistema de Inventário e Economia Dinâmica
O jogo substitui o sistema tradicional de subida automática de nível (XP) por uma mecânica de coleta, gerenciada por uma bolsa invisível dividida em duas carteiras:

1. **Inventário Mineral:** Armazena Minério Comum, Minério Raro, Cristais e Madeira, obtidos ao destruir blocos ou derrotar inimigos. É utilizado nas compras do Ferreiro.
2. **Inventário Orgânico:** Armazena Plasma, Essência Fantasmal, Esporos, Núcleo de Esporos, Chapéu de Cogumelo, Gosma, Musgo e Olho de Goblin. É utilizado nas compras do Ambulante Místico.

#### 🏪 NPCs Vendedores (Aparições Aleatórias)
Os vendedores podem aparecer quando a saída é liberada nas fases finais dos quatro primeiros biomas (fases 3, 6, 9 e 12). A quantidade de NPCs depende dos espaços livres encontrados perto da saída:
* **O Ferreiro:** Aceita recursos minerais. Vende melhorias para a força da picareta, alcance das bombas, tempo de recarga e quantidade de bombas simultâneas.
* **O Ambulante Místico:** Aceita recursos orgânicos. Vende melhorias de vida, velocidade, imunidade a veneno, cargas de escudo e poções de cura.

---

### 8. Mecânicas de Combate e Ritmo
O combate é compassado e focado na precisão do posicionamento, inspirado no equilíbrio tático de *Cuphead*:
* **Ataque direcional:** O golpe da picareta cria uma hitbox à frente do jogador. A direção do golpe fica travada durante a animação, mesmo que o jogador vire.
* **Bombas:** A explosão atinge os inimigos e pode destruir pedras e minérios dentro de uma área em losango. O raio inicial é de dois tiles e pode aumentar com melhorias. Cada inimigo recebe dano apenas uma vez por explosão.
* **Knockback:** Inimigos atingidos pela picareta podem ser empurrados; o Golem também consegue empurrar o jogador.

---

### 9. Controles
| Tecla | Ação |
| :--- | :--- |
| **W, A, S, D** | Movimentação |
| **Clique esquerdo** | Atacar com a picareta |
| **Clique direito** | Plantar uma bomba |
| **Esc** | Pausar / voltar |
| **E** | Interagir com NPCs |
| **F11** | Alternar tela cheia |

---

### 10. Estrutura Arquitetural do Projeto (POO)
O projeto é separado por responsabilidades em módulos:

* `main.py`: ponto de entrada do jogo.
* `Blast_Miner.py`: loop principal, fases, câmera, renderização, HUD e gerenciamento de estados.
* `config.py`: constantes compartilhadas, como tamanho dos tiles e fase inicial/final.
* `Mapas/gerador_mapas.py`: geração procedural, validação de caminhos e busca por áreas livres.
* `entidades/`: jogador, inimigos, chefes e NPCs.
* `objetos/`: bombas, projéteis, itens, drops e inventário.
* `telas/`: menu, pausa, diálogo, loja, game over, vitória e estados de navegação entre telas.



## Efeitos sonoros

Os efeitos sonoros ficam em `assets/audio/` e sao carregados por `sons.py`. O jogo tenta inicializar o mixer do Pygame automaticamente. Se o computador estiver sem dispositivo de audio, o jogo continua funcionando normalmente, apenas sem efeitos. Para ajustar o volume, edite o dicionario `_VOLUMES` em `sons.py`. A musica de fundo nao esta incluida.

---

## Sprites adicionais e animações

Os sprites novos ficam em `assets/sprites/integrados/`. As imagens foram separadas das folhas originais, recortadas por quadro e salvas em PNG com transparência. O carregamento e o cache das animações ficam em `entidades/animacoes.py`.

Foram integrados:

- Goblin: animações de parado, caminhada, arremesso de lança e dano.
- Slime: animações de repouso, movimento e dano; os slimes pequenos usam uma escala menor.
- Fantasma: repouso, flutuação, alerta e dano.
- Cogumelos: o cogumelo agressivo usa repouso, caminhada, investida e dano; o cogumelo de esporos alterna entre escondido, alerta e disparo.
- Golens: golem de musgo e golem de lava; o Guardião usa o golem de cristal.
- Mykros: usa a arte do cogumelo agressivo em escala de chefe.
- NPCs: Ferreiro e Ambulante Místico com animação de respiração.
- Itens: ícones próprios para os recursos do inventário.
- Bomba: sprite colocado, aviso piscando e animação da explosão.
- Lança: projétil desenhado com a imagem recortada e rotacionado conforme a direção do disparo.

O personagem do jogador manteve os sprites direcionais que o projeto já utilizava. A folha de picaretas também ficou de fora nesta integração: ela traz poses isoladas, enquanto o jogador atual já possui animações próprias de movimento e ataque. Assim, evitamos trocar uma animação funcional por uma imagem estática.

Depois do primeiro teste, os quadros dos três golens foram recortados novamente para remover o fundo cinza que ficava preso em espaços fechados, como embaixo dos braços. Os quadros de repouso e movimento do slime também foram corrigidos para retirar fragmentos das molduras. O pulo agora mantém uma escala consistente entre os quadros e desloca o corpo para cima no meio do movimento. A duração dos quadros foi aumentada em aproximadamente 35% para deixar as animações mais suaves.

Se algum arquivo de sprite estiver ausente ou não puder ser carregado, as entidades continuam tendo o desenho antigo como alternativa. As animações de morte foram extraídas quando existiam, mas ainda não são reproduzidas: o jogo atual remove o inimigo assim que ele morre. Isso pode ser implementado depois, sem alterar a hitbox nem o sistema de dano atual.
