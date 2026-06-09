# Blast Miner Co.

## 📝 Relatório do Jogo e GDD (Game Design Document)

### 1. Título do Jogo
**Blast Miner Co.** (Edição Roguelite RPG)

### 2. Descrição Geral
Blast Miner Co. é um jogo de **RPG de Ação e Exploração 2D** com visão top-down, desenvolvido em Python utilizando a biblioteca Pygame. Inspirado na atmosfera de exploração orgânica de *Stardew Valley* e nas dinâmicas de combate, salas procedurais e sinergia de itens de *The Binding of Isaac*, o jogo coloca o jogador no papel de um minerador preso em profundezas perigosas e em constante transformação.

### 3. Objetivo do Jogo
O objetivo principal é explorar **12 níveis de profundidade** subterrânea gerados proceduralmente, coletando recursos preciosos, enfrentando hordas de criaturas e comprando equipamentos. Para vencer e cumprir o contrato da corporação, o jogador deve alcançar a profundidade máxima (Andar 12) e derrotar o temível **Golem de Lava (Boss Final)** para revelar a saída definitiva da caverna.

---

### 4. Personagem Principal (Mike)
O protagonista é **Mike**, um minerador dedicado e azarado da Blast Miner Co. 
* **Movimentação:** Livre e contínua pelo cenário (abandonando a movimentação rígida presa a blocos).
* **Atributos Iniciais:**
  * **Vida (HP):** Representada por 3 corações na interface.
  * **Dano e Alcance:** Atributos que determinam a força do ataque físico e a área de colisão da arma.
  * **Velocidade de Movimento:** Velocidade em pixels de deslocamento pela caverna.
  * **Capacidade de Explosivos:** Determina o raio em cruz da dinamite e a velocidade de recarga (*cooldown*) para plantar novas bombas.
* **Direcionamento:** O personagem monitora constantemente para qual dos 4 eixos (Cima, Baixo, Esquerda, Direita) está olhando, influenciando a direção de seus ataques.

---

### 5. Inimigos e Obstáculos
O jogo conta com um ecossistema de criaturas com comportamentos distintos e ataques telegrafados (sinais visuais antes de agir):
* **Fantasmas:** Criaturas etéreas e persistentes. Movem-se de forma contínua e são capazes de atravessar pedras soltas para perseguir o jogador.
* **Cogumelos:** Inimigos focados em controle de área. Fixam-se no solo e expelem esporos ou projéteis venenosos que criam zonas de perigo temporárias no chão.
* **Golems de Pedra:** Monstros robustos e lentos. Possuem um ataque pesado de investida que aplica um violento *knockback* (empurrão) no jogador se for atingido.
* **BOSS: O Golem de Lava (Fase 12):** Um chefe colossal que ocupa múltiplos blocos da matriz, quebra o cenário ao se mover e gera mini-golems para proteger o núcleo vulcânico.

---

### 6. Cenário e Geração Procedural Orgânica
O mapa do jogo abandona os labirintos simétricos e geométricos para criar **cavernas de formato natural**.

* **Algoritmo de Autômatos Celulares:** As paredes rochosas permanentes são geradas simulando processos de erosão natural, criando curvas, salões amplos e reentrâncias.
* **Detritos Soltos:** O chão das salas é livre e aberto. Obstáculos destrutíveis como **Pedras Comuns** e **Veios de Minério Raro** são distribuídos de forma espalhada pelo chão, funcionando como objetos individuais.
* **A Mecânica da Escada Secreta:** Não existem portas fixas nas paredes. No início de cada andar, uma pedra comum é escolhida secretamente pelo gerador para esconder a passagem. Quando o jogador explode a pedra correta, uma **Escada / Buraco de Queda** é revelada no chão, permitindo a descida de nível.
* **Sistema de Spawn Seguro:** Ao descer para uma nova caverna, o Mike cai em uma coordenada de solo limpo totalmente aleatória. Para garantir a justiça do gameplay, os monstros só podem surgir em áreas localizadas fora de um **raio de segurança de 5 blocos** de distância do jogador.

#### 🎨 Progressão de Biomas
O motor visual do jogo lê a profundidade atual e altera dinamicamente a paleta de cores dos blocos:
1. **Bioma 1: Minas de Terra (Fases 1-3 | 50m - 150m):** Tons terrosos e marrons. Desafio focado em pedras comuns e fantasmas.
2. **Bioma 2: Caverna de Fungos (Fases 4-6 | 200m - 350m):** Paredes em tons escuros e musgo verde. Introdução dos perigos venenosos dos cogumelos.
3. **Bioma 3: Minas de Cristal Profundas (Fases 7-9 | 400m - 550m):** Paredes cianas e roxas brilhantes. Alta concentração de veios minerais para acúmulo de riquezas.
4. **Bioma 4: Núcleo Vulcânico (Fases 10-12 | 600m+):** Rochas pretas de obsidiana e rios de lava. A Fase 12 gera uma arena totalmente limpa de blocos no centro para o combate contra o Boss.

---

### 7. Sistema de Inventário e Economia Dinâmica
O jogo substitui o sistema tradicional de subida automática de nível (XP) por uma mecânica de coleta, gerenciada por uma bolsa invisível dividida em duas carteiras:

1. **Inventário Mineral:** Armazena pedras, carvão, ferro e ouro extraídos ao explodir os blocos da caverna. É utilizado como moeda de troca na Forja.
2. **Inventário Orgânico:** Armazena plasmas, esporos e núcleos biológicos deixados fisicamente pelos monstros ao morrerem. É utilizado como moeda com o Ambulante.

#### 🏪 NPCs Vendedores (Aparições Aleatórias)
Durante a jornada entre o nível 1 e o nível 11, dois mercadores independentes surgirão de forma física e aleatória dentro das cavernas de combate, com a garantia de surgirem **no mínimo 3 vezes cada**:
* **O Ferreiro:** Aceita apenas recursos do *Inventário Mineral*. Vende upgrades para o arsenal físico (espadas com maior alcance de corte, aumento do raio da explosão das bombas e pavios mais rápidos).
* **O Ambulante Místico:** Aceita apenas recursos do *Inventário Orgânico*. Vende *buffs* permanentes para os atributos vitais do Mike (recipientes extras de corações de vida, aumento de velocidade de corrida e imunidades a venenos).

---

### 8. Mecânicas de Combate e Ritmo
O combate é compassado e focado na precisão do posicionamento, inspirado no equilíbrio tático de *Cuphead*:
* **Trava de Ação (Action Lock):** Ao desferir um golpe de espada, a velocidade do Mike é zerada por uma fração de segundo (cerca de 10 a 15 frames). O jogador precisa parar para atacar, impedindo ataques desenfreados em corrida.
* **Hitbox da Espada:** O jogo gera uma área de dano invisível na frente do jogador baseada no seu eixo de visão atual.
* **Knockback Geral:** Tanto os inimigos quanto o jogador sofrem um recuo físico (empurrão) imediato ao serem atingidos por ataques ou explosões, gerando janelas táticas de reposicionamento.

---

### 9. Controles
| Tecla | Ação |
| :--- | :--- |
| **W, A, S, D** | Movimentação Livre (Cima, Esquerda, Baixo, Direita) |
| **Clique do Mouse / K_J** | Ataque Direcional com a Espada |
| **Espaço / K_K** | Plantar Dinamite Tática |
| **Esc / P** | Pausar Jogo |
| **E / F** | Interagir com os NPCs Vendedores |

---

### 10. Estrutura Arquitetural do Projeto (POO)
O projeto é estruturado de forma modular utilizando Programação Orientada a Objetos para garantir que novos monstros e itens sejam adicionados com facilidade:
* `main.py`: Inicialização do Pygame, tratamento de eventos do teclado e execução do loop principal do jogo.
* `gerenciador_fases.py`: Controla o fluxo de profundidade, a troca de biomas e o spawn seguro dos personagens.
* `gerador_mapas.py`: Contém a lógica de Autômatos Celulares para esculpir as cavernas orgânicas e esconder a escada.
* `entidades/player.py`: Gerencia a física do Mike, inventário de recursos, estados de trava de movimento e detecção de ataques de espada.
* `entidades/inimigos.py`: Classe base `Inimigo` e suas subclasses derivadas (`Fantasma`, `Cogumelo`, `Golem`, `Boss`), gerenciando IA e tabelas de drops orgânicos.
* `interface/hud.py`: Renderiza os corações de vida, contadores de minérios/essências e avisos de profundidade na tela.
* `interface/lojas.py`: Gerencia os menus interativos e interfaces gráficas ao conversar com o Ferreiro ou Ambulante.