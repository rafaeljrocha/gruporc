from app.config import AppConfig
from app.services import _crud

STATUS_VALIDOS = {"ativo", "inativo", "em_criacao"}


def _normalizar(dados: dict) -> dict:
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise ValueError("Nome do canal é obrigatório")
    plataforma = (dados.get("plataforma") or "").strip()
    if not plataforma:
        raise ValueError("Plataforma é obrigatória")
    status = (dados.get("status") or "ativo").strip() or "ativo"
    if status not in STATUS_VALIDOS:
        raise ValueError("Status de canal inválido")
    seguidores = dados.get("seguidores")
    return {
        "nome": nome,
        "plataforma": plataforma,
        "url_handle": (dados.get("url_handle") or "").strip() or None,
        "seguidores": int(seguidores) if seguidores not in (None, "") else 0,
        "status": status,
        "responsavel": (dados.get("responsavel") or "").strip() or None,
        "observacoes": (dados.get("observacoes") or "").strip() or None,
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "canal_marketing", order_by="nome")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "canal_marketing", _normalizar(dados))


def atualizar(config: AppConfig, canal_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "canal_marketing", canal_id, _normalizar(dados))


def excluir(config: AppConfig, canal_id: int) -> None:
    _crud.excluir(config, "canal_marketing", canal_id)
