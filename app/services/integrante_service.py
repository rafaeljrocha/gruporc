import json

from app.config import AppConfig
from app.database import get_db, row_to_dict, rows_to_dicts

_CAMPOS_TEXTO = [
    "nome", "cpf", "rg", "numero_passaporte", "numero_convenio_saude",
    "tipo_sanguineo", "calcado", "tamanho_calca", "tamanho_camiseta", "tamanho_camisa",
]
_CAMPOS_DATA = ["data_nascimento", "validade_passaporte", "validade_convenio_saude", "biometria_atualizada_em"]
_CAMPOS_NUMERICOS = ["altura_cm", "peso_kg", "medida_cintura", "medida_ombro"]


def _normalizar(dados: dict) -> dict:
    normalizado = {}
    for campo in _CAMPOS_TEXTO:
        valor = dados.get(campo)
        normalizado[campo] = valor.strip() if isinstance(valor, str) else valor
    for campo in _CAMPOS_DATA:
        valor = dados.get(campo)
        normalizado[campo] = valor.strip() if isinstance(valor, str) and valor.strip() else None
    for campo in _CAMPOS_NUMERICOS:
        valor = dados.get(campo)
        normalizado[campo] = float(valor) if valor not in (None, "") else None
    outras_medidas = dados.get("outras_medidas")
    if isinstance(outras_medidas, (dict, list)):
        outras_medidas = json.dumps(outras_medidas)
    normalizado["outras_medidas"] = outras_medidas or None
    if not normalizado.get("nome"):
        raise ValueError("Nome do integrante é obrigatório")
    return normalizado


def listar(config: AppConfig, apenas_ativos: bool = True) -> list[dict]:
    conn = get_db(config)
    try:
        sql = "SELECT * FROM integrante"
        if apenas_ativos:
            sql += " WHERE ativo = 1"
        sql += " ORDER BY nome"
        return rows_to_dicts(conn.execute(sql).fetchall())
    finally:
        conn.close()


def obter(config: AppConfig, integrante_id: int) -> dict | None:
    conn = get_db(config)
    try:
        return row_to_dict(conn.execute("SELECT * FROM integrante WHERE id = ?", (integrante_id,)).fetchone())
    finally:
        conn.close()


def criar(config: AppConfig, dados: dict) -> dict:
    dados = _normalizar(dados)
    conn = get_db(config)
    try:
        colunas = ", ".join(dados.keys())
        placeholders = ", ".join("?" for _ in dados)
        cursor = conn.execute(f"INSERT INTO integrante ({colunas}) VALUES ({placeholders})", list(dados.values()))
        conn.commit()
        return obter(config, cursor.lastrowid)
    finally:
        conn.close()


def atualizar(config: AppConfig, integrante_id: int, dados: dict) -> dict:
    dados = _normalizar(dados)
    conn = get_db(config)
    try:
        atribuicoes = ", ".join(f"{campo} = ?" for campo in dados)
        conn.execute(
            f"UPDATE integrante SET {atribuicoes} WHERE id = ?",
            list(dados.values()) + [integrante_id],
        )
        conn.commit()
        return obter(config, integrante_id)
    finally:
        conn.close()


def atualizar_documento_vinculado(config: AppConfig, integrante_id: int, tipo_documento: str, numero: str | None, validade: str | None) -> None:
    campos_por_tipo = {
        "passaporte": ("numero_passaporte", "validade_passaporte"),
        "convenio": ("numero_convenio_saude", "validade_convenio_saude"),
    }
    if tipo_documento not in campos_por_tipo:
        return
    campo_numero, campo_validade = campos_por_tipo[tipo_documento]
    conn = get_db(config)
    try:
        conn.execute(
            f"UPDATE integrante SET {campo_numero} = ?, {campo_validade} = ? WHERE id = ?",
            (numero, validade, integrante_id),
        )
        conn.commit()
    finally:
        conn.close()


def excluir(config: AppConfig, integrante_id: int) -> None:
    conn = get_db(config)
    try:
        conn.execute("UPDATE integrante SET ativo = 0 WHERE id = ?", (integrante_id,))
        conn.commit()
    finally:
        conn.close()
