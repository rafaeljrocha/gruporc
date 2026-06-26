from app.config import AppConfig
from app.database import get_db, rows_to_dicts
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
        "modulo_slug": (dados.get("modulo_slug") or "secretariado").strip() or "secretariado",
        "projeto_id": int(dados["projeto_id"]) if dados.get("projeto_id") else None,
        "fornecedor": dados["fornecedor"].strip(),
        "fornecedor_id": int(dados["fornecedor_id"]) if dados.get("fornecedor_id") else None,
        "descricao": (dados.get("descricao") or "").strip() or None,
        "categoria": (dados.get("categoria") or "").strip() or None,
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
        "observacoes": (dados.get("observacoes") or "").strip() or None,
    }


def _proximo_numero(config: AppConfig, modulo_slug: str) -> int:
    conn = get_db(config)
    try:
        maior = conn.execute(
            "SELECT MAX(numero) AS maior FROM despesa WHERE modulo_slug = ?", (modulo_slug,)
        ).fetchone()["maior"]
        return (maior or 0) + 1
    finally:
        conn.close()


def listar(config: AppConfig, modulo_slug: str | None = "secretariado", projeto_id: int | None = None) -> list[dict]:
    """Lista despesas. Por compatibilidade, o módulo padrão é 'secretariado'
    (usado pela aba de despesas legada do Secretariado). Os módulos novos
    informam explicitamente o seu modulo_slug."""
    clausulas, params = [], []
    if modulo_slug:
        clausulas.append("d.modulo_slug = ?")
        params.append(modulo_slug)
    if projeto_id:
        clausulas.append("d.projeto_id = ?")
        params.append(projeto_id)
    where = ("WHERE " + " AND ".join(clausulas)) if clausulas else ""
    conn = get_db(config)
    try:
        rows = conn.execute(
            f"""
            SELECT d.*, p.nome AS projeto_nome
            FROM despesa d
            LEFT JOIN projeto p ON p.id = d.projeto_id
            {where}
            ORDER BY d.numero DESC
            """,
            params,
        ).fetchall()
    finally:
        conn.close()
    return rows_to_dicts(rows)


def criar(config: AppConfig, dados: dict) -> dict:
    dados_normalizados = _normalizar(dados)
    dados_normalizados["numero"] = _proximo_numero(config, dados_normalizados["modulo_slug"])
    return _crud.criar(config, "despesa", dados_normalizados)


def atualizar(config: AppConfig, despesa_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "despesa", despesa_id, _normalizar(dados))


def excluir(config: AppConfig, despesa_id: int) -> None:
    _crud.excluir(config, "despesa", despesa_id)
