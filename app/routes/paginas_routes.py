from pathlib import Path

from flask import Blueprint, abort, current_app, render_template, request, send_file, session

from app.auth import login_required

paginas_bp = Blueprint("paginas", __name__)

MODULOS_SISTEMA = [
    {"slug": "secretariado", "nome": "Secretariado Executivo"},
    {"slug": "administrativo", "nome": "Administrativo"},
    {"slug": "rh", "nome": "Recursos Humanos"},
    {"slug": "marketing", "nome": "Marketing"},
    {"slug": "juridico", "nome": "Jurídico"},
    {"slug": "financeiro", "nome": "Financeiro"},
    {"slug": "cursos", "nome": "Cursos"},
]


def _config():
    return current_app.config["SISRITHA_CONFIG"]


def _obter_config_sistema():
    """Retorna configurações globais do sistema (logo, nome, dados)."""
    from app.database import get_db, row_to_dict
    try:
        conn = get_db(_config())
        chaves = ["nome_sistema", "logo_path", "texto_apresentacao",
                  "telefone", "email", "endereco", "site"]
        resultado = {}
        for chave in chaves:
            row = conn.execute(
                "SELECT valor FROM configuracao WHERE chave = ?", (chave,)
            ).fetchone()
            resultado[chave] = row[0] if row else None
        conn.close()
        return resultado
    except Exception:
        return {}


@paginas_bp.context_processor
def injetar_config_sistema():
    """Injeta config_sistema em todos os templates do blueprint."""
    if session.get("usuario_id"):
        return {"config_sistema": _obter_config_sistema()}
    return {"config_sistema": {}}


@paginas_bp.route("/")
@login_required
def home():
    habilitados = session.get("modulos_habilitados", [])
    papel = session.get("papel")
    modulos = []
    for modulo in MODULOS_SISTEMA:
        habilitado = papel == "master" or modulo["slug"] in habilitados
        modulos.append({**modulo, "habilitado": habilitado})
    return render_template("home.html", modulos=modulos, papel=papel)


@paginas_bp.route("/secretariado")
@login_required
def secretariado():
    return render_template("modulos/secretariado/index.html")


@paginas_bp.route("/configuracoes")
@login_required
def configuracoes():
    if session.get("papel") != "master":
        abort(403)
    from app.database import get_db, row_to_dict
    conn = get_db(_config())
    try:
        usuarios = [row_to_dict(r) for r in conn.execute(
            "SELECT id, nome, email, papel, ativo, modulos_habilitados FROM usuario ORDER BY id"
        ).fetchall()]
    finally:
        conn.close()
    return render_template("configuracoes.html", usuarios=usuarios, modulos=MODULOS_SISTEMA)


@paginas_bp.route("/configuracoes-sistema")
@login_required
def configuracoes_sistema():
    if session.get("papel") != "master":
        abort(403)
    config = _obter_config_sistema()
    return render_template("configuracoes_sistema.html", cfg=config)


@paginas_bp.route("/data-arquivo")
@login_required
def data_arquivo():
    config = _config()
    raiz = Path(config.data_dir).resolve()
    caminho = (Path(request.args.get("caminho", ""))).resolve()
    if raiz not in caminho.parents and caminho != raiz:
        abort(403)
    if not caminho.is_file():
        abort(404)
    return send_file(caminho)
