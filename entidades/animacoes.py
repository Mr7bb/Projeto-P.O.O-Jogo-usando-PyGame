import os
import pygame

_DIRETORIO_SPRITES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "sprites", "integrados"
)
_CACHE_ANIMACOES = {}
_CACHE_IMAGENS = {}
_FATOR_DURACAO_ANIMACOES = 1.35


def carregar_animacao(nome, acao, altura, inverter=False, escala_uniforme=False):
    """Carrega quadros em cache, mantendo a proporção original dos desenhos."""
    chave = (nome, acao, altura, inverter, escala_uniforme)
    if chave in _CACHE_ANIMACOES:
        return _CACHE_ANIMACOES[chave]

    diretorio = os.path.join(_DIRETORIO_SPRITES, nome)
    if not os.path.isdir(diretorio):
        _CACHE_ANIMACOES[chave] = ()
        return ()

    arquivos = sorted(
        arquivo for arquivo in os.listdir(diretorio)
        if arquivo.startswith(acao + "_") and arquivo.lower().endswith(".png")
    )
    imagens_originais = []
    for arquivo in arquivos:
        caminho = os.path.join(diretorio, arquivo)
        try:
            imagens_originais.append(pygame.image.load(caminho).convert_alpha())
        except pygame.error as erro:
            print(f"[SPRITES] Falha ao carregar {caminho}: {erro}")

    quadros = []
    altura_referencia = 0
    if altura and escala_uniforme and imagens_originais:
        altura_referencia = sum(imagem.get_height() for imagem in imagens_originais) / len(imagens_originais)

    for imagem in imagens_originais:
        if altura:
            if escala_uniforme and altura_referencia:
                escala = altura / altura_referencia
                largura = max(1, round(imagem.get_width() * escala))
                altura_quadro = max(1, round(imagem.get_height() * escala))
                imagem = pygame.transform.scale(imagem, (largura, altura_quadro))
            else:
                largura = max(1, round(imagem.get_width() * altura / imagem.get_height()))
                imagem = pygame.transform.scale(imagem, (largura, altura))
        if inverter:
            imagem = pygame.transform.flip(imagem, True, False)
        quadros.append(imagem)

    _CACHE_ANIMACOES[chave] = tuple(quadros)
    return _CACHE_ANIMACOES[chave]


def carregar_imagem(caminho_relativo, altura=None):
    """Carrega uma imagem individual e a mantém em cache."""
    chave = (caminho_relativo, altura)
    if chave in _CACHE_IMAGENS:
        return _CACHE_IMAGENS[chave]

    caminho = os.path.join(_DIRETORIO_SPRITES, caminho_relativo)
    try:
        imagem = pygame.image.load(caminho).convert_alpha()
        if altura:
            largura = max(1, round(imagem.get_width() * altura / imagem.get_height()))
            imagem = pygame.transform.scale(imagem, (largura, altura))
        _CACHE_IMAGENS[chave] = imagem
        return imagem
    except (pygame.error, FileNotFoundError) as erro:
        print(f"[SPRITES] Falha ao carregar {caminho}: {erro}")
        _CACHE_IMAGENS[chave] = None
        return None


def desenhar_animacao(tela, entidade, nome, acao, altura, cam_x=0, cam_y=0,
                      intervalo=9, inverter=False, deslocamento_y=0,
                      escala_uniforme=False, deslocamentos_quadros=None):
    """Desenha a animação alinhada pela base, sem alterar a hitbox da entidade."""
    quadros = carregar_animacao(nome, acao, altura, inverter, escala_uniforme)
    if not quadros:
        return False

    acao_atual = (nome, acao, inverter)
    if getattr(entidade, "_sprite_acao_atual", None) != acao_atual:
        entidade._sprite_acao_atual = acao_atual
        entidade._sprite_anim_timer = 0

    timer = getattr(entidade, "_sprite_anim_timer", 0)
    intervalo_real = max(1, round(intervalo * _FATOR_DURACAO_ANIMACOES))
    indice = (timer // intervalo_real) % len(quadros)
    entidade._sprite_anim_timer = timer + 1

    ajuste_y = deslocamento_y
    if deslocamentos_quadros and indice < len(deslocamentos_quadros):
        ajuste_y += deslocamentos_quadros[indice]

    rect = entidade.rect
    sprite = quadros[indice]
    destino = sprite.get_rect(midbottom=(
        rect.centerx - cam_x,
        rect.bottom - cam_y + ajuste_y,
    ))
    tela.blit(sprite, destino)
    return True
