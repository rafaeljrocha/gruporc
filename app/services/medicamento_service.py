import json

from app.config import AppConfig
from app.services import _crud


def _normalizar(dados: dict) -> dict:
    if not dados.get("integrante_id"):
        raise ValueError("Integrante é obrigatório")
    if not (dados.get("nome") or "").strip():
        raise ValueError("Nome do medicamento é obrigatório")
    horarios = dados.get("horarios")
    if isinstance(horarios, list):
        horarios = json.dumps(horarios)
    return {
        "integrante_id": int(dados["integrante_id"]),
        "nome": dados["nome"].strip(),
        "principio_ativo": (dados.get("principio_ativo") or "").strip() or None,
        "dosagem": (dados.get("dosagem") or "").strip() or None,
        "horarios": horarios or None,
        "dias_tratamento": int(dados["dias_tratamento"]) if dados.get("dias_tratamento") else None,
        "uso_continuo": 1 if dados.get("uso_continuo") else 0,
        "data_inicio": (dados.get("data_inicio") or "").strip() or None,
        "ativo": 1 if dados.get("ativo", True) else 0,
    }


def listar_por_integrante(config: AppConfig, integrante_id: int) -> list[dict]:
    return _crud.listar(config, "medicamento", "integrante_id = ?", (integrante_id,), "nome")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "medicamento", _normalizar(dados))


def atualizar(config: AppConfig, medicamento_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "medicamento", medicamento_id, _normalizar(dados))


def excluir(config: AppConfig, medicamento_id: int) -> None:
    _crud.desativar(config, "medicamento", medicamento_id)
