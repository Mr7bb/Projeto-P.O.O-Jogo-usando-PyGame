import os
import pygame

_DIRETORIO_SONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "audio")
_SONS = {}
_ATIVO = False

_VOLUMES = {
    "picareta": 0.42,
    "dano": 0.55,
    "morte": 0.48,
    "projetil": 0.32,
    "explosao": 0.55,
    "aviso_ataque": 0.42,
    "bomba": 0.35,
    "escudo": 0.42,
}

def iniciar_sons():
    """Inicializa o mixer e carrega os efeitos. Se o dispositivo de audio falhar, o jogo continua sem som."""
    global _ATIVO

    if _ATIVO:
        return True

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.set_num_channels(16)

        for nome in _VOLUMES:
            caminho = os.path.join(_DIRETORIO_SONS, f"{nome}.wav")
            if os.path.isfile(caminho):
                som = pygame.mixer.Sound(caminho)
                som.set_volume(_VOLUMES[nome])
                _SONS[nome] = som

        _ATIVO = True
        return True
    except (pygame.error, OSError) as erro:
        _SONS.clear()
        _ATIVO = False
        print(f"[AUDIO] Sons desativados: {erro}")
        return False

def tocar(nome):
    """Toca um efeito carregado. Nunca interrompe o jogo se o audio estiver indisponivel."""
    if not _ATIVO:
        return

    som = _SONS.get(nome)
    if som is not None:
        try:
            som.play()
        except pygame.error:
            pass
