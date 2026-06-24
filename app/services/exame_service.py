from app.config import AppConfig
from app.services import _crud, webhook_service


def _normalizar(dados: dict) -> dict:
    if not dados.get("integrante_id"):
        raise ValueError("Integrante é obrigatório")
    return {
        "integrante_id": int(dados["integrante_id"]),
        "medico_solicitante": (dados.get("medico_solicitante") or "").strip() or None,
        "finalidade": (dados.get("finalidade") or "").strip() or None,
        "data_coleta": (dados.get("data_coleta") or "").strip() or None,
        "horario": (dados.get("horario") or "").strip() or None,
        "laboratorio": (dados.get("laboratorio") or "").strip() or None,
        "endereco_laboratorio": (dados.get("endereco_laboratorio") or "").strip() or None,
        "valor": float(dados["valor"]) if dados.get("valor") not in (None, "") else None,
        "status": (dados.get("status") or "agendado").strip(),
        "resultado_path": dados.get("resultado_path"),
        "google_agenda_id": dados.get("google_agenda_id"),
    }


def listar_por_integrante(config: AppConfig, integrante_id: int) -> list[dict]:
    return _crud.listar(config, "exame", "integrante_id = ?", (integrante_id,), "data_coleta")


def criar(config: AppConfig, dados: dict) -> dict:
    exame = _crud.criar(config, "exame", _normalizar(dados))
    webhook_service.disparar(config, "novo_exame", exame)
    return exame


def atualizar(config: AppConfig, exame_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "exame", exame_id, _normalizar(dados))


def excluir(config: AppConfig, exame_id: int) -> None:
    _crud.excluir(config, "exame", exame_id)
