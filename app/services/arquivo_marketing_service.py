from app.config import AppConfig
from app.services import _crud

TIPOS_VALIDOS = {"imagem", "video", "pdf", "outro"}


def _normalizar(dados: dict) -> dict:
    nome = (dados.get("nome") or "").strip()
    if not nome:
        raise ValueError("Nome do arquivo é obrigatório")
    tipo = (dados.get("tipo_arquivo") or "outro").strip() or "outro"
    if tipo not in TIPOS_VALIDOS:
        tipo = "outro"
    tamanho = dados.get("tamanho_bytes")
    return {
        "nome": nome,
        "tipo_arquivo": tipo,
        "descricao": (dados.get("descricao") or "").strip() or None,
        "tags": (dados.get("tags") or "").strip() or None,
        "caminho_arquivo": dados.get("caminho_arquivo"),
        "nome_arquivo": dados.get("nome_arquivo"),
        "tamanho_bytes": int(tamanho) if tamanho not in (None, "") else None,
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "arquivo_marketing", order_by="created_at DESC")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "arquivo_marketing", _normalizar(dados))


def excluir(config: AppConfig, arquivo_id: int) -> None:
    _crud.excluir(config, "arquivo_marketing", arquivo_id)
