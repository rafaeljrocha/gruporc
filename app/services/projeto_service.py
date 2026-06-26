from app.config import AppConfig
from app.database import get_db, row_to_dict, rows_to_dicts
from app.services import _crud

STATUS_VALIDOS = {"aberto", "concluido", "cancelado"}


def _normalizar(dados: dict) -> dict:
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise ValueError("Nome do projeto é obrigatório")
    status = (dados.get("status") or "aberto").strip() or "aberto"
    if status not in STATUS_VALIDOS:
        raise ValueError("Status de projeto inválido")
    orcamento = dados.get("orcamento")
    return {
        "nome": nome,
        "descricao": (dados.get("descricao") or "").strip() or None,
        "modulo_slug": (dados.get("modulo_slug") or "secretariado").strip() or "secretariado",
        "status": status,
        "data_inicio": (dados.get("data_inicio") or "").strip() or None,
        "data_fim": (dados.get("data_fim") or "").strip() or None,
        "orcamento": float(orcamento) if orcamento not in (None, "") else None,
        "responsavel": (dados.get("responsavel") or "").strip() or None,
    }


def listar(config: AppConfig, modulo_slug: str | None = None) -> list[dict]:
    if modulo_slug:
        return _crud.listar(config, "projeto", "modulo_slug = ?", (modulo_slug,), "created_at DESC")
    return _crud.listar(config, "projeto", order_by="created_at DESC")


def obter(config: AppConfig, projeto_id: int) -> dict | None:
    return _crud.obter(config, "projeto", projeto_id)


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "projeto", _normalizar(dados))


def atualizar(config: AppConfig, projeto_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "projeto", projeto_id, _normalizar(dados))


def remover(config: AppConfig, projeto_id: int) -> None:
    conn = get_db(config)
    try:
        # Desvincular despesas antes de remover o projeto
        conn.execute("UPDATE despesa SET projeto_id = NULL WHERE projeto_id = ?", (projeto_id,))
        conn.execute("DELETE FROM projeto WHERE id = ?", (projeto_id,))
        conn.commit()
    finally:
        conn.close()


def obter_com_despesas(config: AppConfig, projeto_id: int) -> dict | None:
    conn = get_db(config)
    try:
        projeto = row_to_dict(conn.execute("SELECT * FROM projeto WHERE id = ?", (projeto_id,)).fetchone())
        if not projeto:
            return None
        despesas = rows_to_dicts(conn.execute(
            "SELECT * FROM despesa WHERE projeto_id = ? ORDER BY data_servico DESC, id DESC",
            (projeto_id,),
        ).fetchall())
    finally:
        conn.close()
    projeto["despesas"] = despesas
    projeto["total_gasto"] = sum((d.get("valor") or 0) for d in despesas)
    return projeto


def totais_por_projeto(config: AppConfig, modulo_slug: str) -> list[dict]:
    conn = get_db(config)
    try:
        rows = conn.execute(
            """
            SELECT p.id, p.nome, p.descricao, p.status, p.orcamento, p.responsavel,
                   p.data_inicio, p.data_fim,
                   COUNT(d.id) AS qtd_despesas,
                   COALESCE(SUM(d.valor), 0) AS total_gasto
            FROM projeto p
            LEFT JOIN despesa d ON d.projeto_id = p.id
            WHERE p.modulo_slug = ?
            GROUP BY p.id
            ORDER BY p.created_at DESC
            """,
            (modulo_slug,),
        ).fetchall()
    finally:
        conn.close()
    return rows_to_dicts(rows)
