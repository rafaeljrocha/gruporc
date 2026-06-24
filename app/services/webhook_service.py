import requests

from app.config import AppConfig


def disparar(config: AppConfig, tipo: str, dados: dict) -> None:
    url = config.webhook_n8n_url
    if not url:
        return
    try:
        requests.post(url, json={"tipo": tipo, "dados": dados}, timeout=5)
    except Exception:
        pass
