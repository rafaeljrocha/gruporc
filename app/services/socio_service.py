from app.config import AppConfig
from app.services import _crud


def _normalizar(dados: dict) -> dict:
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise ValueError("Nome do sócio é obrigatório")
    percentual = dados.get("percentual")
    return {
        "nome": nome,
        "cpf_passaporte": (dados.get("cpf_passaporte") or "").strip() or None,
        "tipo_pessoa": (dados.get("tipo_pessoa") or "fisica").strip() or "fisica",
        "empresa_id": int(dados["empresa_id"]) if dados.get("empresa_id") else None,
        "percentual": float(percentual) if percentual not in (None, "") else None,
        "cargo": (dados.get("cargo") or "").strip() or None,
        "data_entrada": (dados.get("data_entrada") or "").strip() or None,
        "data_saida": (dados.get("data_saida") or "").strip() or None,
        "ativo": 1 if dados.get("ativo", True) in (True, 1, "1", "true", "on") else 0,
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "socio", order_by="nome")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "socio", _normalizar(dados))


def atualizar(config: AppConfig, socio_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "socio", socio_id, _normalizar(dados))


def excluir(config: AppConfig, socio_id: int) -> None:
    _crud.excluir(config, "socio", socio_id)
