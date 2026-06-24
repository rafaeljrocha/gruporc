from app.config import AppConfig
from app.services import _crud


def _normalizar(dados: dict) -> dict:
    if not dados.get("integrante_id"):
        raise ValueError("Integrante é obrigatório")
    if not (dados.get("emitente") or "").strip():
        raise ValueError("Emitente é obrigatório")
    if not (dados.get("data_emissao") or "").strip():
        raise ValueError("Data de emissão é obrigatória")
    return {
        "integrante_id": int(dados["integrante_id"]),
        "emitente": dados["emitente"].strip(),
        "data_emissao": dados["data_emissao"].strip(),
        "valor": float(dados["valor"]) if dados.get("valor") not in (None, "") else None,
        "caminho_arquivo": dados.get("caminho_arquivo"),
        "nome_arquivo": dados.get("nome_arquivo"),
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "recibo_saude", order_by="data_emissao DESC")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "recibo_saude", _normalizar(dados))


def excluir(config: AppConfig, recibo_id: int) -> None:
    _crud.excluir(config, "recibo_saude", recibo_id)
