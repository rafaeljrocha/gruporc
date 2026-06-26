from flask import Blueprint, current_app, jsonify, request

from app.auth import api_login_required
from app.services import despesa_service, projeto_service, upload_service

despesas_api_bp = Blueprint("despesas_api", __name__, url_prefix="/api")


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


# ---------- Projetos ----------

@despesas_api_bp.route("/projetos", methods=["GET"])
@api_login_required
def listar_projetos():
    modulo_slug = request.args.get("modulo_slug")
    return jsonify(projeto_service.listar(_config(), modulo_slug))


@despesas_api_bp.route("/projetos/totais", methods=["GET"])
@api_login_required
def totais_projetos():
    modulo_slug = request.args.get("modulo_slug", "")
    if not modulo_slug:
        return _erro("modulo_slug é obrigatório")
    return jsonify(projeto_service.totais_por_projeto(_config(), modulo_slug))


@despesas_api_bp.route("/projetos", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_projeto():
    return jsonify(projeto_service.criar(_config(), request.get_json(force=True) or {})), 201


@despesas_api_bp.route("/projetos/<int:projeto_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_projeto(projeto_id):
    return jsonify(projeto_service.atualizar(_config(), projeto_id, request.get_json(force=True) or {}))


@despesas_api_bp.route("/projetos/<int:projeto_id>", methods=["DELETE"])
@api_login_required
def excluir_projeto(projeto_id):
    projeto_service.remover(_config(), projeto_id)
    return jsonify({"ok": True})


@despesas_api_bp.route("/projetos/<int:projeto_id>/despesas", methods=["GET"])
@api_login_required
def despesas_do_projeto(projeto_id):
    projeto = projeto_service.obter_com_despesas(_config(), projeto_id)
    if not projeto:
        return _erro("Projeto não encontrado", 404)
    return jsonify(projeto)


# ---------- Despesas (transversal a módulos / projetos) ----------
# Namespace próprio (/api/modulo-despesas) para não colidir com a aba de
# despesas legada do Secretariado, que usa /api/despesas.

@despesas_api_bp.route("/modulo-despesas", methods=["GET"])
@api_login_required
def listar_despesas_modulo():
    modulo_slug = request.args.get("modulo_slug")
    projeto_id = request.args.get("projeto_id", type=int)
    return jsonify(despesa_service.listar(_config(), modulo_slug, projeto_id))


@despesas_api_bp.route("/modulo-despesas/totais", methods=["GET"])
@api_login_required
def totais_despesas_modulo():
    modulo_slug = request.args.get("modulo_slug", "")
    if not modulo_slug:
        return _erro("modulo_slug é obrigatório")
    return jsonify(projeto_service.totais_por_projeto(_config(), modulo_slug))


@despesas_api_bp.route("/modulo-despesas", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_despesa_modulo():
    dados = request.form.to_dict()
    arquivo = request.files.get("arquivo")
    if arquivo and arquivo.filename:
        subpasta = f"despesas/{dados.get('modulo_slug', 'geral')}"
        caminho, nome = upload_service.salvar_arquivo(_config(), arquivo, subpasta)
        dados["caminho_arquivo"] = caminho
        dados["nome_arquivo"] = nome
    return jsonify(despesa_service.criar(_config(), dados)), 201


@despesas_api_bp.route("/modulo-despesas/<int:despesa_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_despesa_modulo(despesa_id):
    return jsonify(despesa_service.atualizar(_config(), despesa_id, request.get_json(force=True) or {}))


@despesas_api_bp.route("/modulo-despesas/<int:despesa_id>", methods=["DELETE"])
@api_login_required
def excluir_despesa_modulo(despesa_id):
    despesa_service.excluir(_config(), despesa_id)
    return jsonify({"ok": True})
