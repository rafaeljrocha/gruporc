from app.config import AppConfig
from app.database import get_db, row_to_dict


def obter_valor(config: AppConfig, chave: str, padrao: str | None = None) -> str | None:
    conn = get_db(config)
    try:
        linha = conn.execute("SELECT valor FROM configuracao WHERE chave = ?", (chave,)).fetchone()
        return linha["valor"] if linha else padrao
    finally:
        conn.close()


def definir_valor(config: AppConfig, chave: str, valor: str) -> None:
    conn = get_db(config)
    try:
        conn.execute(
            """INSERT INTO configuracao (chave, valor) VALUES (?, ?)
               ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor, updated_at = CURRENT_TIMESTAMP""",
            (chave, valor),
        )
        conn.commit()
    finally:
        conn.close()


def obter_modulo(config: AppConfig, slug: str) -> dict | None:
    conn = get_db(config)
    try:
        return row_to_dict(conn.execute("SELECT * FROM modulo_config WHERE slug = ?", (slug,)).fetchone())
    finally:
        conn.close()


def salvar_modulo(config: AppConfig, slug: str, dados: dict) -> dict:
    conn = get_db(config)
    try:
        existente = conn.execute("SELECT id FROM modulo_config WHERE slug = ?", (slug,)).fetchone()
        if existente:
            conn.execute(
                """UPDATE modulo_config SET nome = ?, logo_path = ?, responsavel = ?,
                   email_contato = ?, telefone_contato = ? WHERE slug = ?""",
                (dados.get("nome"), dados.get("logo_path"), dados.get("responsavel"),
                 dados.get("email_contato"), dados.get("telefone_contato"), slug),
            )
        else:
            conn.execute(
                """INSERT INTO modulo_config (slug, nome, logo_path, responsavel, email_contato, telefone_contato)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (slug, dados.get("nome"), dados.get("logo_path"), dados.get("responsavel"),
                 dados.get("email_contato"), dados.get("telefone_contato")),
            )
        conn.commit()
    finally:
        conn.close()
    return obter_modulo(config, slug)
