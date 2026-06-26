from app.config import AppConfig
from app.services import _crud

STATUS_VALIDOS = {"ideia", "em_producao", "revisao", "agendado", "publicado", "cancelado"}


def _normalizar(dados: dict) -> dict:
    titulo = (dados.get("titulo") or "").strip()
    if not titulo:
        raise ValueError("Título do conteúdo é obrigatório")
    status = (dados.get("status") or "ideia").strip() or "ideia"
    if status not in STATUS_VALIDOS:
        raise ValueError("Status de conteúdo inválido")
    return {
        "titulo": titulo,
        "canal_id": int(dados["canal_id"]) if dados.get("canal_id") else None,
        "formato": (dados.get("formato") or "").strip() or None,
        "data_prevista": (dados.get("data_prevista") or "").strip() or None,
        "data_publicacao": (dados.get("data_publicacao") or "").strip() or None,
        "status": status,
        "tags": (dados.get("tags") or "").strip() or None,
        "descricao": (dados.get("descricao") or "").strip() or None,
        "url_publicado": (dados.get("url_publicado") or "").strip() or None,
        "caminho_arquivo": dados.get("caminho_arquivo"),
        "nome_arquivo": dados.get("nome_arquivo"),
    }


def listar(config: AppConfig) -> list[dict]:
    return _crud.listar(config, "conteudo_marketing", order_by="created_at DESC")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "conteudo_marketing", _normalizar(dados))


def atualizar(config: AppConfig, conteudo_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "conteudo_marketing", conteudo_id, _normalizar(dados))


def excluir(config: AppConfig, conteudo_id: int) -> None:
    _crud.excluir(config, "conteudo_marketing", conteudo_id)
