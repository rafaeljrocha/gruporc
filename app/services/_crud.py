from app.config import AppConfig
from app.database import get_db, row_to_dict, rows_to_dicts


def listar(config: AppConfig, tabela: str, where: str = "", params: tuple = (), order_by: str = "id") -> list[dict]:
    conn = get_db(config)
    try:
        sql = f"SELECT * FROM {tabela}"
        if where:
            sql += f" WHERE {where}"
        sql += f" ORDER BY {order_by}"
        return rows_to_dicts(conn.execute(sql, params).fetchall())
    finally:
        conn.close()


def obter(config: AppConfig, tabela: str, registro_id: int) -> dict | None:
    conn = get_db(config)
    try:
        return row_to_dict(conn.execute(f"SELECT * FROM {tabela} WHERE id = ?", (registro_id,)).fetchone())
    finally:
        conn.close()


def criar(config: AppConfig, tabela: str, dados: dict) -> dict:
    conn = get_db(config)
    try:
        colunas = ", ".join(dados.keys())
        placeholders = ", ".join("?" for _ in dados)
        cursor = conn.execute(f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})", list(dados.values()))
        conn.commit()
        registro_id = cursor.lastrowid
    finally:
        conn.close()
    return obter(config, tabela, registro_id)


def atualizar(config: AppConfig, tabela: str, registro_id: int, dados: dict) -> dict:
    conn = get_db(config)
    try:
        atribuicoes = ", ".join(f"{campo} = ?" for campo in dados)
        conn.execute(f"UPDATE {tabela} SET {atribuicoes} WHERE id = ?", list(dados.values()) + [registro_id])
        conn.commit()
    finally:
        conn.close()
    return obter(config, tabela, registro_id)


def excluir(config: AppConfig, tabela: str, registro_id: int) -> None:
    conn = get_db(config)
    try:
        conn.execute(f"DELETE FROM {tabela} WHERE id = ?", (registro_id,))
        conn.commit()
    finally:
        conn.close()


def desativar(config: AppConfig, tabela: str, registro_id: int) -> None:
    conn = get_db(config)
    try:
        conn.execute(f"UPDATE {tabela} SET ativo = 0 WHERE id = ?", (registro_id,))
        conn.commit()
    finally:
        conn.close()
