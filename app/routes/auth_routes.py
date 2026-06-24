import json

import bcrypt
import pyotp
import qrcode
import io
import base64

from flask import Blueprint, current_app, redirect, render_template, request, session, url_for

from app.database import get_db, row_to_dict
from app.seguranca import registrar_falha, registrar_sucesso, verificar_bloqueio

auth_bp = Blueprint("auth", __name__)


def _config():
    return current_app.config["SISRITHA_CONFIG"]


def _buscar_usuario_por_email(email: str) -> dict | None:
    conn = get_db(_config())
    try:
        return row_to_dict(
            conn.execute("SELECT * FROM usuario WHERE email = ? AND ativo = 1", (email.strip().lower(),)).fetchone()
        )
    finally:
        conn.close()


def _ativar_totp(usuario_id: int, secret: str) -> None:
    conn = get_db(_config())
    try:
        conn.execute(
            "UPDATE usuario SET totp_secret = ?, totp_ativo = 1 WHERE id = ?", (secret, usuario_id)
        )
        conn.commit()
    finally:
        conn.close()


def _iniciar_sessao(usuario: dict) -> None:
    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]
    session["usuario_email"] = usuario["email"]
    session["papel"] = usuario["papel"]
    session["modulos_habilitados"] = json.loads(usuario.get("modulos_habilitados") or "[]")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", erro=None)

    email = (request.form.get("email") or "").strip().lower()
    senha = request.form.get("senha") or ""

    restante = verificar_bloqueio(email)
    if restante:
        minutos = max(1, restante // 60)
        return render_template("login.html", erro=f"Conta bloqueada. Tente novamente em {minutos} min.")

    usuario = _buscar_usuario_por_email(email)
    senha_valida = usuario and bcrypt.checkpw(senha.encode(), usuario["senha_hash"].encode())

    if not senha_valida:
        registrar_falha(email, _config())
        return render_template("login.html", erro="Email ou senha inválidos.")

    registrar_sucesso(email)
    session["pendente_usuario_id"] = usuario["id"]
    return redirect(url_for("auth.duplo_fator"))


@auth_bp.route("/2fa", methods=["GET", "POST"])
def duplo_fator():
    usuario_id = session.get("pendente_usuario_id")
    if not usuario_id:
        return redirect(url_for("auth.login"))

    conn = get_db(_config())
    try:
        usuario = row_to_dict(conn.execute("SELECT * FROM usuario WHERE id = ?", (usuario_id,)).fetchone())
    finally:
        conn.close()

    if not usuario:
        session.pop("pendente_usuario_id", None)
        return redirect(url_for("auth.login"))

    primeiro_acesso = not usuario["totp_ativo"]

    if request.method == "GET":
        qr_base64 = None
        secret = usuario.get("totp_secret")
        if primeiro_acesso:
            if not secret:
                secret = pyotp.random_base32()
                conn = get_db(_config())
                try:
                    conn.execute("UPDATE usuario SET totp_secret = ? WHERE id = ?", (secret, usuario_id))
                    conn.commit()
                finally:
                    conn.close()
            uri = pyotp.totp.TOTP(secret).provisioning_uri(name=usuario["email"], issuer_name="SISRITHA")
            imagem = qrcode.make(uri)
            buffer = io.BytesIO()
            imagem.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        return render_template("login.html", etapa_2fa=True, primeiro_acesso=primeiro_acesso, qr_base64=qr_base64, erro=None)

    codigo = (request.form.get("codigo") or "").strip()
    secret = usuario.get("totp_secret")
    totp = pyotp.TOTP(secret)
    if not secret or not totp.verify(codigo, valid_window=1):
        return render_template("login.html", etapa_2fa=True, primeiro_acesso=primeiro_acesso, qr_base64=None, erro="Código inválido.")

    if primeiro_acesso:
        _ativar_totp(usuario_id, secret)

    session.pop("pendente_usuario_id", None)
    _iniciar_sessao(usuario)
    return redirect(url_for("paginas.home"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
