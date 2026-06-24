from app.config import AppConfig
from app.services import _crud


def _normalizar(dados: dict) -> dict:
    if not dados.get("integrante_id"):
        raise ValueError("Integrante é obrigatório")
    return {
        "integrante_id": int(dados["integrante_id"]),
        "medico_nome": (dados.get("medico_nome") or "").strip() or None,
        "especialidade": (dados.get("especialidade") or "").strip() or None,
        "finalidade": (dados.get("finalidade") or "").strip() or None,
        "data_receita": (dados.get("data_receita") or "").strip() or None,
        "caminho_arquivo": dados.get("caminho_arquivo"),
        "nome_arquivo": dados.get("nome_arquivo"),
    }


def listar_por_integrante(config: AppConfig, integrante_id: int) -> list[dict]:
    return _crud.listar(config, "receita_medica", "integrante_id = ?", (integrante_id,), "data_receita")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "receita_medica", _normalizar(dados))


def excluir(config: AppConfig, receita_id: int) -> None:
    _crud.excluir(config, "receita_medica", receita_id)
