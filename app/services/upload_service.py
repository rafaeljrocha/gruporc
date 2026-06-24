import uuid
from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.config import AppConfig

EXTENSOES_PERMITIDAS = {"pdf", "png", "jpg", "jpeg"}


def _salvar_em(base_dir: str, arquivo: FileStorage, subpasta: str) -> tuple[str, str]:
    nome_original = secure_filename(arquivo.filename or "arquivo")
    extensao = nome_original.rsplit(".", 1)[-1].lower() if "." in nome_original else ""
    if extensao not in EXTENSOES_PERMITIDAS:
        raise ValueError("Tipo de arquivo não permitido")
    nome_unico = f"{uuid.uuid4().hex}_{nome_original}"
    destino_dir = Path(base_dir) / subpasta
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / nome_unico
    arquivo.save(destino)
    return str(destino), nome_original


def salvar_arquivo(config: AppConfig, arquivo: FileStorage, subpasta: str) -> tuple[str, str]:
    return _salvar_em(config.documentos_dir, arquivo, subpasta)


def salvar_logo(config: AppConfig, arquivo: FileStorage, subpasta: str) -> tuple[str, str]:
    return _salvar_em(config.logos_dir, arquivo, subpasta)
