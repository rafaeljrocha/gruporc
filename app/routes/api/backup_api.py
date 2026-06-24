from flask import Blueprint, current_app, jsonify

from app.auth import master_required
from app.services import backup_service

backup_api_bp = Blueprint("backup_api", __name__, url_prefix="/api")


@backup_api_bp.route("/backup/gerar", methods=["GET"])
@master_required
def gerar_backup():
    config = current_app.config["SISRITHA_CONFIG"]
    nome_arquivo = backup_service.gerar_backup(config)
    return jsonify({"arquivo": nome_arquivo})
