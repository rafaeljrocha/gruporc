from datetime import date

from flask import Blueprint, current_app, jsonify, request

from app.auth import api_login_required, master_required
from app.services import (
    contrato_service,
    documento_adm_service,
    empresa_service,
    obrigacao_service,
    socio_service,
    upload_service,
    webhook_service,
    configuracao_service,
)

administrativo_api_bp = Blueprint("administrativo_api", __name__, url_prefix="/api")


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


def _dias_para(data_str: str | None) -> int | None:
    if not data_str:
        return None
    try:
        alvo = date.fromisoformat(str(data_str)[:10])
    except ValueError:
        return None
    return (alvo - date.today()).days


# ---------- Empresas ----------

@administrativo_api_bp.route("/empresas", methods=["GET"])
@api_login_required
def listar_empresas():
    return jsonify(empresa_service.listar(_config()))


@administrativo_api_bp.route("/empresas", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_empresa():
    dados = request.form.to_dict()
    logo = request.files.get("logo")
    if logo and logo.filename:
        caminho, _nome = upload_service.salvar_logo(_config(), logo, "empresas")
        dados["logo_path"] = caminho
    return jsonify(empresa_service.criar(_config(), dados)), 201


@administrativo_api_bp.route("/empresas/<int:empresa_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_empresa(empresa_id):
    return jsonify(empresa_service.atualizar(_config(), empresa_id, request.get_json(force=True) or {}))


@administrativo_api_bp.route("/empresas/<int:empresa_id>", methods=["DELETE"])
@api_login_required
def excluir_empresa(empresa_id):
    empresa_service.excluir(_config(), empresa_id)
    return jsonify({"ok": True})


# ---------- Sócios ----------

@administrativo_api_bp.route("/socios", methods=["GET"])
@api_login_required
def listar_socios():
    return jsonify(socio_service.listar(_config()))


@administrativo_api_bp.route("/socios", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_socio():
    return jsonify(socio_service.criar(_config(), request.get_json(force=True) or {})), 201


@administrativo_api_bp.route("/socios/<int:socio_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_socio(socio_id):
    return jsonify(socio_service.atualizar(_config(), socio_id, request.get_json(force=True) or {}))


@administrativo_api_bp.route("/socios/<int:socio_id>", methods=["DELETE"])
@api_login_required
def excluir_socio(socio_id):
    socio_service.excluir(_config(), socio_id)
    return jsonify({"ok": True})


# ---------- Contratos ----------

@administrativo_api_bp.route("/contratos", methods=["GET"])
@api_login_required
def listar_contratos():
    return jsonify(contrato_service.listar(_config()))


@administrativo_api_bp.route("/contratos", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_contrato():
    dados = request.form.to_dict()
    arquivo = request.files.get("arquivo")
    if arquivo and arquivo.filename:
        caminho, nome = upload_service.salvar_arquivo(_config(), arquivo, "contratos")
        dados["caminho_arquivo"] = caminho
        dados["nome_arquivo"] = nome
    return jsonify(contrato_service.criar(_config(), dados)), 201


@administrativo_api_bp.route("/contratos/<int:contrato_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_contrato(contrato_id):
    return jsonify(contrato_service.atualizar(_config(), contrato_id, request.get_json(force=True) or {}))


@administrativo_api_bp.route("/contratos/<int:contrato_id>", methods=["DELETE"])
@api_login_required
def excluir_contrato(contrato_id):
    contrato_service.excluir(_config(), contrato_id)
    return jsonify({"ok": True})


# ---------- Documentos ----------

@administrativo_api_bp.route("/documentos-adm", methods=["GET"])
@api_login_required
def listar_documentos_adm():
    return jsonify(documento_adm_service.listar(_config()))


@administrativo_api_bp.route("/documentos-adm", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_documento_adm():
    dados = request.form.to_dict()
    arquivo = request.files.get("arquivo")
    if arquivo and arquivo.filename:
        caminho, nome = upload_service.salvar_arquivo(_config(), arquivo, "documentos_adm")
        dados["caminho_arquivo"] = caminho
        dados["nome_arquivo"] = nome
    return jsonify(documento_adm_service.criar(_config(), dados)), 201


@administrativo_api_bp.route("/documentos-adm/<int:documento_id>", methods=["DELETE"])
@api_login_required
def excluir_documento_adm(documento_id):
    documento_adm_service.excluir(_config(), documento_id)
    return jsonify({"ok": True})


# ---------- Obrigações ----------

@administrativo_api_bp.route("/obrigacoes", methods=["GET"])
@api_login_required
def listar_obrigacoes():
    return jsonify(obrigacao_service.listar(_config()))


@administrativo_api_bp.route("/obrigacoes", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_obrigacao():
    obrigacao = obrigacao_service.criar(_config(), request.get_json(force=True) or {})
    dias = _dias_para(obrigacao.get("proximo_vencimento"))
    if dias is not None and dias <= 7:
        webhook_service.disparar(_config(), "alerta_obrigacao", obrigacao)
    return jsonify(obrigacao), 201


@administrativo_api_bp.route("/obrigacoes/<int:obrigacao_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_obrigacao(obrigacao_id):
    return jsonify(obrigacao_service.atualizar(_config(), obrigacao_id, request.get_json(force=True) or {}))


@administrativo_api_bp.route("/obrigacoes/<int:obrigacao_id>", methods=["DELETE"])
@api_login_required
def excluir_obrigacao(obrigacao_id):
    obrigacao_service.excluir(_config(), obrigacao_id)
    return jsonify({"ok": True})


# ---------- Configurações do módulo (master only) ----------

@administrativo_api_bp.route("/administrativo/configuracoes", methods=["GET"])
@api_login_required
def obter_configuracoes_administrativo():
    return jsonify(configuracao_service.obter_modulo(_config(), "administrativo") or {})


@administrativo_api_bp.route("/administrativo/configuracoes", methods=["PUT"])
@master_required
@_tratar_valueerror
def salvar_configuracoes_administrativo():
    dados = request.form.to_dict()
    logo = request.files.get("logo")
    if logo and logo.filename:
        caminho, _nome = upload_service.salvar_logo(_config(), logo, "administrativo")
        dados["logo_path"] = caminho
    return jsonify(configuracao_service.salvar_modulo(_config(), "administrativo", dados))
