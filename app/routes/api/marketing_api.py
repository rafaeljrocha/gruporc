import os
import uuid
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from app.auth import api_login_required, master_required
from app.services import (
    arquivo_marketing_service,
    campanha_service,
    canal_service,
    conteudo_service,
    metrica_service,
    upload_service,
    configuracao_service,
)

marketing_api_bp = Blueprint("marketing_api", __name__, url_prefix="/api")


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


# ---------- Canais ----------

@marketing_api_bp.route("/canais", methods=["GET"])
@api_login_required
def listar_canais():
    return jsonify(canal_service.listar(_config()))


@marketing_api_bp.route("/canais", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_canal():
    return jsonify(canal_service.criar(_config(), request.get_json(force=True) or {})), 201


@marketing_api_bp.route("/canais/<int:canal_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_canal(canal_id):
    return jsonify(canal_service.atualizar(_config(), canal_id, request.get_json(force=True) or {}))


@marketing_api_bp.route("/canais/<int:canal_id>", methods=["DELETE"])
@api_login_required
def excluir_canal(canal_id):
    canal_service.excluir(_config(), canal_id)
    return jsonify({"ok": True})


# ---------- Conteúdo ----------

@marketing_api_bp.route("/conteudos", methods=["GET"])
@api_login_required
def listar_conteudos():
    return jsonify(conteudo_service.listar(_config()))


@marketing_api_bp.route("/conteudos", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_conteudo():
    dados = request.form.to_dict()
    arquivo = request.files.get("arquivo")
    if arquivo and arquivo.filename:
        caminho, nome = upload_service.salvar_arquivo(_config(), arquivo, "marketing/conteudos")
        dados["caminho_arquivo"] = caminho
        dados["nome_arquivo"] = nome
    return jsonify(conteudo_service.criar(_config(), dados)), 201


@marketing_api_bp.route("/conteudos/<int:conteudo_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_conteudo(conteudo_id):
    return jsonify(conteudo_service.atualizar(_config(), conteudo_id, request.get_json(force=True) or {}))


@marketing_api_bp.route("/conteudos/<int:conteudo_id>", methods=["DELETE"])
@api_login_required
def excluir_conteudo(conteudo_id):
    conteudo_service.excluir(_config(), conteudo_id)
    return jsonify({"ok": True})


# ---------- Campanhas ----------

@marketing_api_bp.route("/campanhas", methods=["GET"])
@api_login_required
def listar_campanhas():
    return jsonify(campanha_service.listar(_config()))


@marketing_api_bp.route("/campanhas", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_campanha():
    return jsonify(campanha_service.criar(_config(), request.get_json(force=True) or {})), 201


@marketing_api_bp.route("/campanhas/<int:campanha_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_campanha(campanha_id):
    return jsonify(campanha_service.atualizar(_config(), campanha_id, request.get_json(force=True) or {}))


@marketing_api_bp.route("/campanhas/<int:campanha_id>", methods=["DELETE"])
@api_login_required
def excluir_campanha(campanha_id):
    campanha_service.excluir(_config(), campanha_id)
    return jsonify({"ok": True})


# ---------- Métricas ----------

@marketing_api_bp.route("/metricas", methods=["GET"])
@api_login_required
def listar_metricas():
    return jsonify(metrica_service.listar(_config()))


@marketing_api_bp.route("/metricas", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_metrica():
    return jsonify(metrica_service.criar(_config(), request.get_json(force=True) or {})), 201


@marketing_api_bp.route("/metricas/<int:metrica_id>", methods=["PUT"])
@api_login_required
@_tratar_valueerror
def atualizar_metrica(metrica_id):
    return jsonify(metrica_service.atualizar(_config(), metrica_id, request.get_json(force=True) or {}))


@marketing_api_bp.route("/metricas/<int:metrica_id>", methods=["DELETE"])
@api_login_required
def excluir_metrica(metrica_id):
    metrica_service.excluir(_config(), metrica_id)
    return jsonify({"ok": True})


# ---------- Arquivos (mídia: imagem / vídeo / pdf / outro) ----------

@marketing_api_bp.route("/arquivos-marketing", methods=["GET"])
@api_login_required
def listar_arquivos_marketing():
    return jsonify(arquivo_marketing_service.listar(_config()))


@marketing_api_bp.route("/arquivos-marketing", methods=["POST"])
@api_login_required
@_tratar_valueerror
def criar_arquivo_marketing():
    dados = request.form.to_dict()
    arquivo = request.files.get("arquivo")
    if arquivo and arquivo.filename:
        destino_dir = Path(_config().data_dir) / "marketing" / "arquivos"
        destino_dir.mkdir(parents=True, exist_ok=True)
        nome_original = secure_filename(arquivo.filename)
        nome_unico = f"{uuid.uuid4().hex}_{nome_original}"
        caminho = destino_dir / nome_unico
        arquivo.save(str(caminho))
        dados["caminho_arquivo"] = str(caminho)
        dados["nome_arquivo"] = nome_original
        dados["tamanho_bytes"] = os.path.getsize(caminho)
        if not (dados.get("nome") or "").strip():
            dados["nome"] = nome_original
    return jsonify(arquivo_marketing_service.criar(_config(), dados)), 201


@marketing_api_bp.route("/arquivos-marketing/<int:arquivo_id>", methods=["DELETE"])
@api_login_required
def excluir_arquivo_marketing(arquivo_id):
    arquivo_marketing_service.excluir(_config(), arquivo_id)
    return jsonify({"ok": True})


# ---------- Configurações do módulo (master only) ----------

@marketing_api_bp.route("/marketing/configuracoes", methods=["GET"])
@api_login_required
def obter_configuracoes_marketing():
    return jsonify(configuracao_service.obter_modulo(_config(), "marketing") or {})


@marketing_api_bp.route("/marketing/configuracoes", methods=["PUT"])
@master_required
@_tratar_valueerror
def salvar_configuracoes_marketing():
    dados = request.form.to_dict()
    logo = request.files.get("logo")
    if logo and logo.filename:
        caminho, _nome = upload_service.salvar_logo(_config(), logo, "marketing")
        dados["logo_path"] = caminho
    return jsonify(configuracao_service.salvar_modulo(_config(), "marketing", dados))
