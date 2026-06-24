from app.config import AppConfig
from app.services import _crud

STATUS_VALIDOS = {"solicitado", "em_analise", "aprovado", "rejeitado", "pago"}


def _normalizar(dados: dict) -> dict:
    if not dados.get("integrante_id"):
        raise ValueError("Integrante é obrigatório")
    if not (dados.get("data_pedido") or "").strip():
        raise ValueError("Data do pedido é obrigatória")
    status = (dados.get("status") or "solicitado").strip()
    if status not in STATUS_VALIDOS:
        raise ValueError("Status de reembolso inválido")
    return {
        "recibo_id": int(dados["recibo_id"]) if dados.get("recibo_id") else None,
        "integrante_id": int(dados["integrante_id"]),
        "data_pedido": dados["data_pedido"].strip(),
        "valor_solicitado": float(dados["valor_solicitado"]) if dados.get("valor_solicitado") not in (None, "") else None,
        "status": status,
        "data_pagamento": (dados.get("data_pagamento") or "").strip() or None,
        "valor_pago": float(dados["valor_pago"]) if dados.get("valor_pago") not in (None, "") else None,
        "observacoes": (dados.get("observacoes") or "").strip() or None,
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "reembolso", order_by="data_pedido DESC")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "reembolso", _normalizar(dados))


def atualizar(config: AppConfig, reembolso_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "reembolso", reembolso_id, _normalizar(dados))


def excluir(config: AppConfig, reembolso_id: int) -> None:
    _crud.excluir(config, "reembolso", reembolso_id)
