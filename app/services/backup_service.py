import shutil
from datetime import datetime
from pathlib import Path

from app.config import AppConfig

MAX_BACKUPS = 10


def gerar_backup(config: AppConfig) -> str:
    nome_arquivo = f"sisritha_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    destino = Path(config.backups_dir) / nome_arquivo
    shutil.copy2(config.db_path, destino)
    _limpar_antigos(config)
    return nome_arquivo


def _limpar_antigos(config: AppConfig) -> None:
    backups = sorted(Path(config.backups_dir).glob("sisritha_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for antigo in backups[MAX_BACKUPS:]:
        antigo.unlink(missing_ok=True)
