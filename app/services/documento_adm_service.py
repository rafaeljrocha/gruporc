from app.config import AppConfig
from app.services import _crud


def _normalizar(dados: dict) -> dict:
    tipo = (dados.get("tipo_documento") or "").strip()
    if not tipo:
        raise ValueError("Tipo de documento é obrigatório")
    return {
        "empresa_id": int(dados["empresa_id"]) if dados.get("empresa_id") else None,
        "tipo_documento": tipo,
        "descricao": (dados.get("descricao") or "").strip() or None,
        "validade": (dados.get("validade") or "").strip() or None,
        "caminho_arquivo": dados.get("caminho_arquivo"),
        "nome_arquivo": dados.get("nome_arquivo"),
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "documento_adm", order_by="created_at DESC")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "documento_adm", _normalizar(dados))


def atualizar(config: AppConfig, documento_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "documento_adm", documento_id, _normalizar(dados))


def excluir(config: AppConfig, documento_id: int) -> None:
    _crud.excluir(config, "documento_adm", documento_id)
