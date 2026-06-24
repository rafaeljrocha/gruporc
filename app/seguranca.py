import time
from collections import defaultdict
from threading import Lock

from app.config import AppConfig

_tentativas: dict[str, list[float]] = defaultdict(list)
_bloqueios: dict[str, float] = {}
_lock = Lock()


def _chave(identificador: str) -> str:
    return identificador.strip().lower()


def verificar_bloqueio(identificador: str) -> int:
    """Retorna segundos restantes de bloqueio (0 se não bloqueado)."""
    chave = _chave(identificador)
    with _lock:
        expira_em = _bloqueios.get(chave)
        if expira_em is None:
            return 0
        restante = expira_em - time.time()
        if restante <= 0:
            _bloqueios.pop(chave, None)
            _tentativas.pop(chave, None)
            return 0
        return int(restante)


def registrar_falha(identificador: str, config: AppConfig) -> int:
    """Registra uma tentativa falha; retorna segundos de bloqueio se acabou de bloquear."""
    chave = _chave(identificador)
    agora = time.time()
    with _lock:
        janela_inicio = agora - config.login_janela_seg
        tentativas = [t for t in _tentativas[chave] if t >= janela_inicio]
        tentativas.append(agora)
        _tentativas[chave] = tentativas
        if len(tentativas) >= config.login_max_tentativas:
            _bloqueios[chave] = agora + config.login_bloqueio_seg
            return config.login_bloqueio_seg
    return 0


def registrar_sucesso(identificador: str) -> None:
    chave = _chave(identificador)
    with _lock:
        _tentativas.pop(chave, None)
        _bloqueios.pop(chave, None)
