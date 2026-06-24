from flask import Blueprint, current_app, jsonify, request

from app.auth import api_login_required, master_required
from app.services import (
    consulta_service,
    despesa_service,
    documento_service,
    exame_service,
    fornecedor_service,
    integrante_service,
    medicamento_service,
    recibo_service,
    receita_service,
    reembolso_service,
    upload_service,
    viagem_service,
    configuracao_service,
)

secretariado_api_bp = Blueprint("secretariado_api", __name__, url_prefix="/api")


def _config():
    return current_app.config["SISRITHA_CONFIG"]


def _erro(mensagem: str, status: int = 400):
    return jsonify({"erro": mensagem}), status


def _tratar_valueerror(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as exc:
            return _erro(str(exc), 422)

    wrapper.__name__ = func.__name__
    return wrapper


# ---------- Integrantes ----------

@secretariado_api_bp.route("/integrantes", methods=["GET"])
@api_login_required
def listar_integrantes():
    return jsonify(integrante_service.listar(_config()))


@secretariado_api_bp.route("/integrantes", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_integrante():
    return jsonify(integrante_service.criar(_config(), request.get_json(force=True) or {})), 201


@secretariado_api_bp.route("/integrantes/<int:integrante_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_integrante(integrante_id):
    return jsonify(integrante_service.atualizar(_config(), integrante_id, request.get_json(force=True) or {}))


@secretariado_api_bp.route("/integrantes/<int:integrante_id>", methods=["DELETE"])
@api_login_required
def excluir_integrante(integrante_id):
    integrante_service.excluir(_config(), integrante_id)
    return jsonify({"ok": True})


# ---------- Documentos (Carteira Digital) ----------

@secretariado_api_bp.route("/integrantes/<int:integrante_id>/documentos", methods=["GET"])
@api_login_required
def listar_documentos(integrante_id):
    return jsonify(documento_service.listar_por_integrante(_config(), integrante_id))


@secretariado_api_bp.route("/documentos", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_documento():
    dados = request.form.to_dict()
    arquivo = request.files.get("arquivo")
    if arquivo and arquivo.filename:
        caminho, nome = upload_service.salvar_arquivo(_config(), arquivo, f"integrante_{dados.get('integrante_id')}")
        dados["caminho_arquivo"] = caminho
        dados["nome_arquivo"] = nome
    return jsonify(documento_service.criar(_config(), dados)), 201


@secretariado_api_bp.route("/documentos/<int:documento_id>", methods=["DELETE"])
@api_login_required
def excluir_documento(documento_id):
    documento_service.excluir(_config(), documento_id)
    return jsonify({"ok": True})


# ---------- Medicamentos ----------

@secretariado_api_bp.route("/integrantes/<int:integrante_id>/medicamentos", methods=["GET"])
@api_login_required
def listar_medicamentos(integrante_id):
    return jsonify(medicamento_service.listar_por_integrante(_config(), integrante_id))


@secretariado_api_bp.route("/medicamentos", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_medicamento():
    return jsonify(medicamento_service.criar(_config(), request.get_json(force=True) or {})), 201


@secretariado_api_bp.route("/medicamentos/<int:medicamento_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_medicamento(medicamento_id):
    return jsonify(medicamento_service.atualizar(_config(), medicamento_id, request.get_json(force=True) or {}))


@secretariado_api_bp.route("/medicamentos/<int:medicamento_id>", methods=["DELETE"])
@api_login_required
def excluir_medicamento(medicamento_id):
    medicamento_service.excluir(_config(), medicamento_id)
    return jsonify({"ok": True})


# ---------- Consultas ----------

@secretariado_api_bp.route("/integrantes/<int:integrante_id>/consultas", methods=["GET"])
@api_login_required
def listar_consultas(integrante_id):
    return jsonify(consulta_service.listar_por_integrante(_config(), integrante_id))


@secretariado_api_bp.route("/consultas", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_consulta():
    return jsonify(consulta_service.criar(_config(), request.get_json(force=True) or {})), 201


@secretariado_api_bp.route("/consultas/<int:consulta_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_consulta(consulta_id):
    return jsonify(consulta_service.atualizar(_config(), consulta_id, request.get_json(force=True) or {}))


@secretariado_api_bp.route("/consultas/<int:consulta_id>", methods=["DELETE"])
@api_login_required
def excluir_consulta(consulta_id):
    consulta_service.excluir(_config(), consulta_id)
    return jsonify({"ok": True})


# ---------- Exames ----------

@secretariado_api_bp.route("/integrantes/<int:integrante_id>/exames", methods=["GET"])
@api_login_required
def listar_exames(integrante_id):
    return jsonify(exame_service.listar_por_integrante(_config(), integrante_id))


@secretariado_api_bp.route("/exames", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_exame():
    return jsonify(exame_service.criar(_config(), request.get_json(force=True) or {})), 201


@secretariado_api_bp.route("/exames/<int:exame_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_exame(exame_id):
    return jsonify(exame_service.atualizar(_config(), exame_id, request.get_json(force=True) or {}))


@secretariado_api_bp.route("/exames/<int:exame_id>", methods=["DELETE"])
@api_login_required
def excluir_exame(exame_id):
    exame_service.excluir(_config(), exame_id)
    return jsonify({"ok": True})


# ---------- Receitas médicas ----------

@secretariado_api_bp.route("/integrantes/<int:integrante_id>/receitas", methods=["GET"])
@api_login_required
def listar_receitas(integrante_id):
    return jsonify(receita_service.listar_por_integrante(_config(), integrante_id))


@secretariado_api_bp.route("/receitas", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_receita():
    dados = request.form.to_dict()
    arquivo = request.files.get("arquivo")
    if arquivo and arquivo.filename:
        caminho, nome = upload_service.salvar_arquivo(_config(), arquivo, f"integrante_{dados.get('integrante_id')}")
        dados["caminho_arquivo"] = caminho
        dados["nome_arquivo"] = nome
    return jsonify(receita_service.criar(_config(), dados)), 201


@secretariado_api_bp.route("/receitas/<int:receita_id>", methods=["DELETE"])
@api_login_required
def excluir_receita(receita_id):
    receita_service.excluir(_config(), receita_id)
    return jsonify({"ok": True})


# ---------- Recibos de saúde ----------

@secretariado_api_bp.route("/recibos", methods=["GET"])
@api_login_required
def listar_recibos():
    return jsonify(recibo_service.listar(_config()))


@secretariado_api_bp.route("/recibos", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_recibo():
    dados = request.form.to_dict()
    arquivo = request.files.get("arquivo")
    if arquivo and arquivo.filename:
        caminho, nome = upload_service.salvar_arquivo(_config(), arquivo, f"integrante_{dados.get('integrante_id')}")
        dados["caminho_arquivo"] = caminho
        dados["nome_arquivo"] = nome
    return jsonify(recibo_service.criar(_config(), dados)), 201


@secretariado_api_bp.route("/recibos/<int:recibo_id>", methods=["DELETE"])
@api_login_required
def excluir_recibo(recibo_id):
    recibo_service.excluir(_config(), recibo_id)
    return jsonify({"ok": True})


# ---------- Reembolsos ----------

@secretariado_api_bp.route("/reembolsos", methods=["GET"])
@api_login_required
def listar_reembolsos():
    return jsonify(reembolso_service.listar(_config()))


@secretariado_api_bp.route("/reembolsos", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_reembolso():
    return jsonify(reembolso_service.criar(_config(), request.get_json(force=True) or {})), 201


@secretariado_api_bp.route("/reembolsos/<int:reembolso_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_reembolso(reembolso_id):
    return jsonify(reembolso_service.atualizar(_config(), reembolso_id, request.get_json(force=True) or {}))


@secretariado_api_bp.route("/reembolsos/<int:reembolso_id>", methods=["DELETE"])
@api_login_required
def excluir_reembolso(reembolso_id):
    reembolso_service.excluir(_config(), reembolso_id)
    return jsonify({"ok": True})


# ---------- Viagens ----------

@secretariado_api_bp.route("/viagens", methods=["GET"])
@api_login_required
def listar_viagens():
    return jsonify(viagem_service.listar(_config()))


@secretariado_api_bp.route("/viagens", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_viagem():
    return jsonify(viagem_service.criar(_config(), request.get_json(force=True) or {})), 201


@secretariado_api_bp.route("/viagens/<int:viagem_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_viagem(viagem_id):
    return jsonify(viagem_service.atualizar(_config(), viagem_id, request.get_json(force=True) or {}))


@secretariado_api_bp.route("/viagens/<int:viagem_id>", methods=["DELETE"])
@api_login_required
def excluir_viagem(viagem_id):
    viagem_service.excluir(_config(), viagem_id)
    return jsonify({"ok": True})


# ---------- Despesas ----------

@secretariado_api_bp.route("/despesas", methods=["GET"])
@api_login_required
def listar_despesas():
    return jsonify(despesa_service.listar(_config()))


@secretariado_api_bp.route("/despesas", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_despesa():
    dados = request.form.to_dict()
    arquivo = request.files.get("arquivo")
    if arquivo and arquivo.filename:
        caminho, nome = upload_service.salvar_arquivo(_config(), arquivo, "despesas")
        dados["caminho_arquivo"] = caminho
        dados["nome_arquivo"] = nome
    return jsonify(despesa_service.criar(_config(), dados)), 201


@secretariado_api_bp.route("/despesas/<int:despesa_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_despesa(despesa_id):
    return jsonify(despesa_service.atualizar(_config(), despesa_id, request.get_json(force=True) or {}))


@secretariado_api_bp.route("/despesas/<int:despesa_id>", methods=["DELETE"])
@api_login_required
def excluir_despesa(despesa_id):
    despesa_service.excluir(_config(), despesa_id)
    return jsonify({"ok": True})


# ---------- Fornecedores ----------

@secretariado_api_bp.route("/fornecedores", methods=["GET"])
@api_login_required
def listar_fornecedores():
    return jsonify(fornecedor_service.listar(_config()))


@secretariado_api_bp.route("/fornecedores", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_fornecedor():
    return jsonify(fornecedor_service.criar(_config(), request.get_json(force=True) or {})), 201


@secretariado_api_bp.route("/fornecedores/<int:fornecedor_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_fornecedor(fornecedor_id):
    return jsonify(fornecedor_service.atualizar(_config(), fornecedor_id, request.get_json(force=True) or {}))


@secretariado_api_bp.route("/fornecedores/<int:fornecedor_id>", methods=["DELETE"])
@api_login_required
def excluir_fornecedor(fornecedor_id):
    fornecedor_service.excluir(_config(), fornecedor_id)
    return jsonify({"ok": True})


# ---------- Configurações do módulo (master only) ----------

@secretariado_api_bp.route("/secretariado/configuracoes", methods=["GET"])
@api_login_required
def obter_configuracoes_secretariado():
    modulo = configuracao_service.obter_modulo(_config(), "secretariado") or {}
    webhook_url = configuracao_service.obter_valor(_config(), "webhook_n8n_url", "")
    return jsonify({**modulo, "webhook_n8n_url": webhook_url})


@secretariado_api_bp.route("/secretariado/configuracoes", methods=["PUT"])
@master_required
@_tratar_valueerror
def salvar_configuracoes_secretariado():
    dados = request.form.to_dict()
    logo = request.files.get("logo")
    if logo and logo.filename:
        caminho, _nome = upload_service.salvar_logo(_config(), logo, "secretariado")
        dados["logo_path"] = caminho
    modulo = configuracao_service.salvar_modulo(_config(), "secretariado", dados)
    if "webhook_n8n_url" in dados:
        configuracao_service.definir_valor(_config(), "webhook_n8n_url", dados["webhook_n8n_url"].strip())
    return jsonify(modulo)


# ── Usuários (master only) ────────────────────────────────────────────────────

@secretariado_api_bp.route("/usuarios", methods=["POST"])
@master_required
def criar_usuario():
    import bcrypt as _bcrypt
    from app.database import get_db, row_to_dict
    dados = request.get_json() or {}
    nome = (dados.get("nome") or "").strip()
    email = (dados.get("email") or "").strip().lower()
    senha = (dados.get("senha") or "").strip()
    papel = dados.get("papel", "padrao")
    ativo = int(dados.get("ativo", 1))
    modulos = dados.get("modulos_habilitados", "[]")
    if not nome or not email:
        return jsonify({"erro": "Nome e email são obrigatórios"}), 400
    if not senha or len(senha) < 10:
        return jsonify({"erro": "Senha deve ter pelo menos 10 caracteres"}), 400
    senha_hash = _bcrypt.hashpw(senha.encode(), _bcrypt.gensalt()).decode()
    conn = get_db(_config())
    try:
        existe = conn.execute("SELECT id FROM usuario WHERE email = ?", (email,)).fetchone()
        if existe:
            return jsonify({"erro": "Email já cadastrado"}), 409
        cur = conn.execute(
            "INSERT INTO usuario (nome, email, senha_hash, papel, ativo, modulos_habilitados) VALUES (?,?,?,?,?,?)",
            (nome, email, senha_hash, papel, ativo, modulos)
        )
        conn.commit()
        u = row_to_dict(conn.execute("SELECT id, nome, email, papel, ativo FROM usuario WHERE id = ?", (cur.lastrowid,)).fetchone())
    finally:
        conn.close()
    return jsonify(u), 201


@secretariado_api_bp.route("/usuarios/<int:uid>", methods=["PUT"])
@master_required
def atualizar_usuario(uid):
    import bcrypt as _bcrypt
    from app.database import get_db, row_to_dict
    dados = request.get_json() or {}
    nome = (dados.get("nome") or "").strip()
    email = (dados.get("email") or "").strip().lower()
    senha = (dados.get("senha") or "").strip()
    papel = dados.get("papel", "padrao")
    ativo = int(dados.get("ativo", 1))
    modulos = dados.get("modulos_habilitados", "[]")
    if not nome or not email:
        return jsonify({"erro": "Nome e email são obrigatórios"}), 400
    conn = get_db(_config())
    try:
        u = conn.execute("SELECT id FROM usuario WHERE id = ?", (uid,)).fetchone()
        if not u:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        if senha:
            if len(senha) < 10:
                return jsonify({"erro": "Senha deve ter pelo menos 10 caracteres"}), 400
            senha_hash = _bcrypt.hashpw(senha.encode(), _bcrypt.gensalt()).decode()
            conn.execute(
                "UPDATE usuario SET nome=?, email=?, senha_hash=?, papel=?, ativo=?, modulos_habilitados=? WHERE id=?",
                (nome, email, senha_hash, papel, ativo, modulos, uid)
            )
        else:
            conn.execute(
                "UPDATE usuario SET nome=?, email=?, papel=?, ativo=?, modulos_habilitados=? WHERE id=?",
                (nome, email, papel, ativo, modulos, uid)
            )
        conn.commit()
        u = row_to_dict(conn.execute("SELECT id, nome, email, papel, ativo FROM usuario WHERE id = ?", (uid,)).fetchone())
    finally:
        conn.close()
    return jsonify(u)


@secretariado_api_bp.route("/usuarios/alterar-senha", methods=["POST"])
@api_login_required
def alterar_senha_proprio():
    import bcrypt as _bcrypt
    from flask import session as _session
    from app.database import get_db
    dados = request.get_json() or {}
    nova = (dados.get("nova_senha") or "").strip()
    if len(nova) < 10:
        return jsonify({"erro": "Senha deve ter pelo menos 10 caracteres"}), 400
    uid = _session.get("usuario_id")
    senha_hash = _bcrypt.hashpw(nova.encode(), _bcrypt.gensalt()).decode()
    conn = get_db(_config())
    try:
        conn.execute("UPDATE usuario SET senha_hash = ? WHERE id = ?", (senha_hash, uid))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})
