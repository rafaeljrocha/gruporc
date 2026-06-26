from app.config import AppConfig
from app.services import _crud

STATUS_VALIDOS = {"vigente", "em_elaboracao", "renovado", "rescindido", "encerrado"}


def _normalizar(dados: dict) -> dict:
    objeto = (dados.get("objeto") or "").strip()
    if not objeto:
        raise ValueError("Objeto do contrato é obrigatório")
    status = (dados.get("status") or "vigente").strip() or "vigente"
    if status not in STATUS_VALIDOS:
        raise ValueError("Status de contrato inválido")
    valor = dados.get("valor")
    return {
        "numero": (dados.get("numero") or "").strip() or None,
        "objeto": objeto,
        "empresa_id": int(dados["empresa_id"]) if dados.get("empresa_id") else None,
        "contraparte": (dados.get("contraparte") or "").strip() or None,
        "valor": float(valor) if valor not in (None, "") else None,
        "data_inicio": (dados.get("data_inicio") or "").strip() or None,
        "data_fim": (dados.get("data_fim") or "").strip() or None,
        "renovacao_automatica": 1 if dados.get("renovacao_automatica") in (True, 1, "1", "true", "on") else 0,
        "status": status,
        "caminho_arquivo": dados.get("caminho_arquivo"),
        "nome_arquivo": dados.get("nome_arquivo"),
        "observacoes": (dados.get("observacoes") or "").strip() or None,
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "contrato", order_by="created_at DESC")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "contrato", _normalizar(dados))


def atualizar(config: AppConfig, contrato_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "contrato", contrato_id, _normalizar(dados))


def excluir(config: AppConfig, contrato_id: int) -> None:
    _crud.excluir(config, "contrato", contrato_id)
