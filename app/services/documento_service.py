from app.config import AppConfig
from app.services import _crud, integrante_service

TIPOS_VALIDOS = {"passaporte", "rg", "cnh", "convenio", "cert_casamento", "cert_nascimento", "outro"}


def _normalizar(dados: dict) -> dict:
    integrante_id = dados.get("integrante_id")
    tipo_documento = (dados.get("tipo_documento") or "").strip()
    if not integrante_id:
        raise ValueError("Integrante é obrigatório")
    if tipo_documento not in TIPOS_VALIDOS:
        raise ValueError("Tipo de documento inválido")
    return {
        "integrante_id": int(integrante_id),
        "tipo_documento": tipo_documento,
        "descricao": (dados.get("descricao") or "").strip() or None,
        "validade": (dados.get("validade") or "").strip() or None,
        "caminho_arquivo": dados.get("caminho_arquivo"),
        "nome_arquivo": dados.get("nome_arquivo"),
    }


def listar_por_integrante(config: AppConfig, integrante_id: int) -> list[dict]:
    return _crud.listar(config, "documento_digital", "integrante_id = ?", (integrante_id,), "validade")


def criar(config: AppConfig, dados: dict) -> dict:
    dados = _normalizar(dados)
    documento = _crud.criar(config, "documento_digital", dados)
    if dados["tipo_documento"] in ("passaporte", "convenio"):
        integrante_service.atualizar_documento_vinculado(
            config, dados["integrante_id"], dados["tipo_documento"], dados.get("descricao"), dados.get("validade")
        )
    return documento


def excluir(config: AppConfig, documento_id: int) -> None:
    _crud.excluir(config, "documento_digital", documento_id)
