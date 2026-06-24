from app.config import AppConfig
from app.services import _crud, webhook_service


def _normalizar(dados: dict) -> dict:
    if not dados.get("integrante_id"):
        raise ValueError("Integrante é obrigatório")
    if not (dados.get("medico_nome") or "").strip():
        raise ValueError("Nome do médico é obrigatório")
    if not (dados.get("data_consulta") or "").strip():
        raise ValueError("Data da consulta é obrigatória")
    return {
        "integrante_id": int(dados["integrante_id"]),
        "medico_nome": dados["medico_nome"].strip(),
        "especialidade": (dados.get("especialidade") or "").strip() or None,
        "crm": (dados.get("crm") or "").strip() or None,
        "data_consulta": dados["data_consulta"].strip(),
        "horario": (dados.get("horario") or "").strip() or None,
        "telefone": (dados.get("telefone") or "").strip() or None,
        "endereco": (dados.get("endereco") or "").strip() or None,
        "email": (dados.get("email") or "").strip() or None,
        "valor": float(dados["valor"]) if dados.get("valor") not in (None, "") else None,
        "status": (dados.get("status") or "agendada").strip(),
        "google_agenda_id": dados.get("google_agenda_id"),
    }


def listar_por_integrante(config: AppConfig, integrante_id: int) -> list[dict]:
    return _crud.listar(config, "consulta", "integrante_id = ?", (integrante_id,), "data_consulta")


def criar(config: AppConfig, dados: dict) -> dict:
    consulta = _crud.criar(config, "consulta", _normalizar(dados))
    webhook_service.disparar(config, "nova_consulta", consulta)
    return consulta


def atualizar(config: AppConfig, consulta_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "consulta", consulta_id, _normalizar(dados))


def excluir(config: AppConfig, consulta_id: int) -> None:
    _crud.excluir(config, "consulta", consulta_id)
