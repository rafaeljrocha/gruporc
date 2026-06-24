from app.config import AppConfig
from app.services import _crud

CATEGORIAS_VALIDAS = {
    "medico", "diarista", "jardineiro", "motorista", "mecanico", "agente_viagem",
    "cozinheiro", "professor", "piscineiro", "baba", "outro",
}


def _normalizar(dados: dict) -> dict:
    if not (dados.get("nome") or "").strip():
        raise ValueError("Nome do fornecedor é obrigatório")
    categoria = (dados.get("categoria") or "").strip() or None
    if categoria and categoria not in CATEGORIAS_VALIDAS:
        raise ValueError("Categoria de fornecedor inválida")
    return {
        "nome": dados["nome"].strip(),
        "telefone": (dados.get("telefone") or "").strip() or None,
        "email": (dados.get("email") or "").strip() or None,
        "descricao": (dados.get("descricao") or "").strip() or None,
        "categoria": categoria,
        "chave_pix": (dados.get("chave_pix") or "").strip() or None,
        "endereco": (dados.get("endereco") or "").strip() or None,
        "ativo": 1 if dados.get("ativo", True) else 0,
    }


def listar(config: AppConfig, apenas_ativos: bool = False) -> list[dict]:
    where = "ativo = 1" if apenas_ativos else ""
    return _crud.listar(config, "fornecedor", where, (), "nome")


def criar(config: AppConfig, dados: dict) -> dict:
    return _crud.criar(config, "fornecedor", _normalizar(dados))


def atualizar(config: AppConfig, fornecedor_id: int, dados: dict) -> dict:
    return _crud.atualizar(config, "fornecedor", fornecedor_id, _normalizar(dados))


def excluir(config: AppConfig, fornecedor_id: int) -> None:
    _crud.desativar(config, "fornecedor", fornecedor_id)
