import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path


def _gerar_ou_ler_secret_key(data_dir: str) -> str:
    env_key = os.environ.get("SECRET_KEY", "").strip()
    if env_key:
        return env_key
    chave_path = Path(data_dir) / ".secret_key"
    if chave_path.exists():
        return chave_path.read_text().strip()
    chave_path.parent.mkdir(parents=True, exist_ok=True)
    nova_chave = secrets.token_hex(32)
    chave_path.write_text(nova_chave)
    return nova_chave


@dataclass
class AppConfig:
    data_dir: str
    db_path: str
    anexos_dir: str
    backups_dir: str
    logos_dir: str
    documentos_dir: str
    secret_key: str
    app_host: str
    app_port: int
    gunicorn_workers: int
    session_lifetime_min: int
    cookies_seguros: bool
    proxy_fix: bool
    webhook_n8n_url: str
    upload_max_mb: int
    senha_min: int
    login_max_tentativas: int
    login_janela_seg: int
    login_bloqueio_seg: int

    @classmethod
    def from_env(cls) -> "AppConfig":
        data_dir = os.environ.get("DATA_DIR", "/data")
        anexos_dir = os.path.join(data_dir, "anexos")
        backups_dir = os.path.join(data_dir, "backups")
        logos_dir = os.path.join(data_dir, "logos")
        documentos_dir = os.path.join(data_dir, "documentos")
        for diretorio in (data_dir, anexos_dir, backups_dir, logos_dir, documentos_dir):
            Path(diretorio).mkdir(parents=True, exist_ok=True)
        return cls(
            data_dir=data_dir,
            db_path=os.path.join(data_dir, "sisritha.db"),
            anexos_dir=anexos_dir,
            backups_dir=backups_dir,
            logos_dir=logos_dir,
            documentos_dir=documentos_dir,
            secret_key=_gerar_ou_ler_secret_key(data_dir),
            app_host=os.environ.get("APP_HOST", "0.0.0.0"),
            app_port=int(os.environ.get("APP_PORT", "8000")),
            gunicorn_workers=int(os.environ.get("GUNICORN_WORKERS", "2")),
            session_lifetime_min=int(os.environ.get("SESSION_LIFETIME_MIN", "60")),
            cookies_seguros=os.environ.get("COOKIES_SEGUROS", "1") == "1",
            proxy_fix=os.environ.get("PROXY_FIX", "1") == "1",
            webhook_n8n_url=os.environ.get("WEBHOOK_N8N_URL", "").strip(),
            upload_max_mb=int(os.environ.get("UPLOAD_MAX_MB", "32")),
            senha_min=int(os.environ.get("SENHA_MIN", "10")),
            login_max_tentativas=int(os.environ.get("LOGIN_MAX_TENTATIVAS", "5")),
            login_janela_seg=int(os.environ.get("LOGIN_JANELA_SEG", "900")),
            login_bloqueio_seg=int(os.environ.get("LOGIN_BLOQUEIO_SEG", "900")),
        )


AppConfig.default = AppConfig.from_env
