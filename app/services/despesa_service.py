from app.config import AppConfig
from app.database import get_db
from app.services import _crud

MODOS_VALIDOS = {"pix", "boleto", "transferencia", "parceria", "cartao", "dinheiro"}


def _normalizar(dados: dict) -> dict:
    if not (dados.get("fornecedor") or "").strip():
        raise ValueError("Fornecedor é obrigatório")
    if dados.get("valor") in (None, ""):
        raise ValueError("Valor é obrigatório")
    modo_pagamento = (dados.get("modo_pagamento") or "").strip() or None
    if modo_pagamento and modo_pagamento not in MODOS_VALIDOS:
        raise ValueError("Modo de pagamento inválido")
    return {
        "fornecedor": dados["fornecedor"].strip(),
        "valor": float(dados["valor"]),
        "data_servico": (dados.get("data_servico") or "").strip() or None,
        "data_vencimento": (dados.get("data_vencimento") or "").strip() or None,
        "modo_pagamento": modo_pagamento,
        "especificacao_parceria": (dados.get("especificacao_parceria") or "").strip() or None,
        "chave_pix": (dados.get("chave_pix") or "").strip() or None,
        "caminho_arquivo": dados.get("caminho_arquivo"),
        "nome_arquivo": dados.get("nome_arquivo"),
        "integrante_id": int(dados["integrante_id"]) if dados.get("integrante_id") else None,
        "status_pagamento": (dados.get("status_pagamento") or "pendente").strip(),
    }


def _proximo_numero(config: AppConfig) -> int:
    conn = get_db(config)
    try:
        maior = conn.execute("SELECT MAX(numero) AS maior FROM despesa").fetchone()["maior"]
        return (maior or 0) + 1
    finally:
        conn.close()


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "despesa", order_by="numero DESC")


def criar(config: AppConfig, dados: dict) -> dict:
    dados_normalizados = _normalizar(dados)
    dados_normalizados["numero"] = _proximo_numero(config)
    return _crud.criar(config, "despesa", dados_normalizados)


def atualizar(config: AppConfig, despesa_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "despesa", despesa_id, _normalizar(dados))


def excluir(config: AppConfig, despesa_id: int) -> None:
    _crud.excluir(config, "despesa", despesa_id)
