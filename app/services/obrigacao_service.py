from app.config import AppConfig
from app.services import _crud

PERIODICIDADES_VALIDAS = {"mensal", "trimestral", "semestral", "anual", "unica"}
STATUS_VALIDOS = {"pendente", "cumprida", "atrasada"}


def _normalizar(dados: dict) -> dict:
    descricao = (dados.get("descricao") or "").strip()
    if not descricao:
        raise ValueError("Descrição da obrigação é obrigatória")
    periodicidade = (dados.get("periodicidade") or "anual").strip() or "anual"
    if periodicidade not in PERIODICIDADES_VALIDAS:
        raise ValueError("Periodicidade inválida")
    status = (dados.get("status") or "pendente").strip() or "pendente"
    if status not in STATUS_VALIDOS:
        raise ValueError("Status de obrigação inválido")
    return {
        "empresa_id": int(dados["empresa_id"]) if dados.get("empresa_id") else None,
        "descricao": descricao,
        "periodicidade": periodicidade,
        "proximo_vencimento": (dados.get("proximo_vencimento") or "").strip() or None,
        "responsavel": (dados.get("responsavel") or "").strip() or None,
        "status": status,
        "observacoes": (dados.get("observacoes") or "").strip() or None,
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "obrigacao", order_by="proximo_vencimento")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "obrigacao", _normalizar(dados))


def atualizar(config: AppConfig, obrigacao_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "obrigacao", obrigacao_id, _normalizar(dados))


def excluir(config: AppConfig, obrigacao_id: int) -> None:
    _crud.excluir(config, "obrigacao", obrigacao_id)
