import json

from app.config import AppConfig
from app.services import _crud

STATUS_VALIDOS = {"planejada", "ativa", "pausada", "encerrada"}


def _normalizar(dados: dict) -> dict:
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise ValueError("Nome da campanha é obrigatório")
    status = (dados.get("status") or "planejada").strip() or "planejada"
    if status not in STATUS_VALIDOS:
        raise ValueError("Status de campanha inválido")
    canais = dados.get("canais")
    if isinstance(canais, (list, dict)):
        canais = json.dumps(canais)
    elif not (canais or "").strip():
        canais = "[]"
    orcamento = dados.get("orcamento")
    return {
        "nome": nome,
        "objetivo": (dados.get("objetivo") or "").strip() or None,
        "canais": canais,
        "orcamento": float(orcamento) if orcamento not in (None, "") else None,
        "data_inicio": (dados.get("data_inicio") or "").strip() or None,
        "data_fim": (dados.get("data_fim") or "").strip() or None,
        "status": status,
        "resultado": (dados.get("resultado") or "").strip() or None,
        "observacoes": (dados.get("observacoes") or "").strip() or None,
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "campanha_marketing", order_by="created_at DESC")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "campanha_marketing", _normalizar(dados))


def atualizar(config: AppConfig, campanha_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "campanha_marketing", campanha_id, _normalizar(dados))


def excluir(config: AppConfig, campanha_id: int) -> None:
    _crud.excluir(config, "campanha_marketing", campanha_id)
