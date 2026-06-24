import json
import sqlite3
from pathlib import Path

import bcrypt

from app.config import AppConfig

_SCHEMA_PATH = Path(__file__).parent / "db" / "schema.sql"

MASTER_EMAIL = "admin@sisritha.local"
MASTER_SENHA = "Admin@2025!"
MODULOS_PADRAO = ["secretariado", "administrativo", "rh", "marketing", "juridico", "financeiro", "cursos"]


def get_db(config: AppConfig) -> sqlite3.Connection:
    conn = sqlite3.connect(config.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]


def init_db(config: AppConfig) -> None:
    conn = get_db(config)
    try:
        conn.executescript(_SCHEMA_PATH.read_text())
        conn.commit()
        _criar_usuario_master(conn)
        conn.commit()
    finally:
        conn.close()


def _criar_usuario_master(conn: sqlite3.Connection) -> None:
    total = conn.execute("SELECT COUNT(*) AS total FROM usuario").fetchone()["total"]
    if total > 0:
        return
    senha_hash = bcrypt.hashpw(MASTER_SENHA.encode(), bcrypt.gensalt()).decode()
    conn.execute(
        """INSERT INTO usuario (nome, email, senha_hash, papel, modulos_habilitados, ativo)
           VALUES (?, ?, ?, 'master', ?, 1)""",
        ("Administrador", MASTER_EMAIL, senha_hash, json.dumps(MODULOS_PADRAO)),
    )
