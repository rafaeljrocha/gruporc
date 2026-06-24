from functools import wraps

from flask import current_app, jsonify, redirect, request, session, url_for


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapper


def api_login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            return jsonify({"erro": "Não autenticado"}), 401
        return view(*args, **kwargs)

    return wrapper


def master_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            if request.path.startswith("/api/"):
                return jsonify({"erro": "Não autenticado"}), 401
            return redirect(url_for("auth.login"))
        if session.get("papel") != "master":
            if request.path.startswith("/api/"):
                return jsonify({"erro": "Acesso restrito ao usuário master"}), 403
            return "Acesso restrito ao usuário master", 403
        return view(*args, **kwargs)

    return wrapper


def usuario_logado() -> dict | None:
    if not session.get("usuario_id"):
        return None
    return {
        "id": session.get("usuario_id"),
        "nome": session.get("usuario_nome"),
        "email": session.get("usuario_email"),
        "papel": session.get("papel"),
        "modulos_habilitados": session.get("modulos_habilitados", []),
    }
