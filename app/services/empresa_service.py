from app.config import AppConfig
from app.services import _crud

TIPOS_VALIDOS = {"ltda", "sa", "mei", "slu", "holding", "offshore", "outro"}
STATUS_VALIDOS = {"ativa", "inativa", "em_constituicao", "encerrada"}


def _normalizar(dados: dict) -> dict:
    razao = (dados.get("razao_social") or "").strip()
    if not razao:
        raise ValueError("Razão social é obrigatória")
    tipo = (dados.get("tipo") or "ltda").strip() or "ltda"
    if tipo not in TIPOS_VALIDOS:
        raise ValueError("Tipo de empresa inválido")
    status = (dados.get("status") or "ativa").strip() or "ativa"
    if status not in STATUS_VALIDOS:
        raise ValueError("Status de empresa inválido")
    capital = dados.get("capital_social")
    return {
        "razao_social": razao,
        "nome_fantasia": (dados.get("nome_fantasia") or "").strip() or None,
        "cnpj": (dados.get("cnpj") or "").strip() or None,
        "tipo": tipo,
        "pais": (dados.get("pais") or "Brasil").strip() or "Brasil",
        "estado": (dados.get("estado") or "").strip() or None,
        "cidade": (dados.get("cidade") or "").strip() or None,
        "endereco": (dados.get("endereco") or "").strip() or None,
        "cep": (dados.get("cep") or "").strip() or None,
        "email": (dados.get("email") or "").strip() or None,
        "telefone": (dados.get("telefone") or "").strip() or None,
        "site": (dados.get("site") or "").strip() or None,
        "objeto_social": (dados.get("objeto_social") or "").strip() or None,
        "capital_social": float(capital) if capital not in (None, "") else None,
        "data_constituicao": (dados.get("data_constituicao") or "").strip() or None,
        "data_encerramento": (dados.get("data_encerramento") or "").strip() or None,
        "status": status,
        "observacoes": (dados.get("observacoes") or "").strip() or None,
        "logo_path": dados.get("logo_path") or None,
        "ativo": 1 if dados.get("ativo", True) in (True, 1, "1", "true", "on") else 0,
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "empresa", order_by="razao_social")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "empresa", _normalizar(dados))


def atualizar(config: AppConfig, empresa_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "empresa", empresa_id, _normalizar(dados))


def excluir(config: AppConfig, empresa_id: int) -> None:
    _crud.excluir(config, "empresa", empresa_id)
