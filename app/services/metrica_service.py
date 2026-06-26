from app.config import AppConfig
from app.database import get_db, rows_to_dicts
from app.services import _crud


def _int(valor):
    return int(valor) if valor not in (None, "") else None


def _float(valor):
    return float(valor) if valor not in (None, "") else None


def _normalizar(dados: dict) -> dict:
    if not dados.get("canal_id"):
        raise ValueError("Canal é obrigatório")
    return {
        "canal_id": int(dados["canal_id"]),
        "periodo_mes": _int(dados.get("periodo_mes")),
        "periodo_ano": _int(dados.get("periodo_ano")),
        "seguidores": _int(dados.get("seguidores")),
        "alcance": _int(dados.get("alcance")),
        "impressoes": _int(dados.get("impressoes")),
        "engajamento": _float(dados.get("engajamento")),
        "cliques": _int(dados.get("cliques")),
        "conversoes": _int(dados.get("conversoes")),
        "observacoes": (dados.get("observacoes") or "").strip() or None,
    }


def listar(config: AppConfig) -> list[dict]:
    conn = get_db(config)
    try:
        rows = conn.execute(
            """
            SELECT m.*, c.nome AS canal_nome
            FROM metrica_marketing m
            LEFT JOIN canal_marketing c ON c.id = m.canal_id
            ORDER BY m.periodo_ano DESC, m.periodo_mes DESC, m.id DESC
            """
        ).fetchall()
    finally:
        conn.close()
    return rows_to_dicts(rows)


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "metrica_marketing", _normalizar(dados))


def atualizar(config: AppConfig, metrica_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "metrica_marketing", metrica_id, _normalizar(dados))


def excluir(config: AppConfig, metrica_id: int) -> None:
    _crud.excluir(config, "metrica_marketing", metrica_id)
