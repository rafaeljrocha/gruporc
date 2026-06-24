from app.config import AppConfig
from app.database import get_db
from app.services import _crud, webhook_service

STATUS_VALIDOS = {"a_comprar", "comprado", "remarcado", "expirado"}


def _normalizar(dados: dict) -> dict:
    status = (dados.get("status") or "a_comprar").strip()
    if status not in STATUS_VALIDOS:
        raise ValueError("Status de viagem inválido")
    return {
        "finalidade": (dados.get("finalidade") or "pessoal").strip(),
        "origem": (dados.get("origem") or "").strip() or None,
        "destino": (dados.get("destino") or "").strip() or None,
        "aeroporto_partida": (dados.get("aeroporto_partida") or "").strip() or None,
        "aeroporto_chegada": (dados.get("aeroporto_chegada") or "").strip() or None,
        "data_ida": (dados.get("data_ida") or "").strip() or None,
        "horario_ida": (dados.get("horario_ida") or "").strip() or None,
        "data_volta": (dados.get("data_volta") or "").strip() or None,
        "horario_volta": (dados.get("horario_volta") or "").strip() or None,
        "numero_passageiros": int(dados.get("numero_passageiros") or 1),
        "valor_compra": float(dados["valor_compra"]) if dados.get("valor_compra") not in (None, "") else None,
        "status": status,
        "agente_nome": (dados.get("agente_nome") or "").strip() or None,
        "agente_telefone": (dados.get("agente_telefone") or "").strip() or None,
        "hotel_nome": (dados.get("hotel_nome") or "").strip() or None,
        "hotel_endereco": (dados.get("hotel_endereco") or "").strip() or None,
        "hotel_telefone": (dados.get("hotel_telefone") or "").strip() or None,
        "hotel_checkin": (dados.get("hotel_checkin") or "").strip() or None,
        "hotel_checkout": (dados.get("hotel_checkout") or "").strip() or None,
        "google_agenda_id": dados.get("google_agenda_id"),
    }


def _salvar_passageiros(config: AppConfig, viagem_id: int, passageiros_ids: list[int]) -> None:
    conn = get_db(config)
    try:
        conn.execute("DELETE FROM viagem_passageiro WHERE viagem_id = ?", (viagem_id,))
        for integrante_id in passageiros_ids:
            conn.execute(
                "INSERT INTO viagem_passageiro (viagem_id, integrante_id) VALUES (?, ?)",
                (viagem_id, int(integrante_id)),
            )
        conn.commit()
    finally:
        conn.close()


def listar(config: AppConfig) -> list[dict]:
    viagens = _crud.listar(config, "viagem", order_by="data_ida DESC")
    conn = get_db(config)
    try:
        for viagem in viagens:
            linhas = conn.execute(
                "SELECT integrante_id FROM viagem_passageiro WHERE viagem_id = ?", (viagem["id"],)
            ).fetchall()
            viagem["passageiros_ids"] = [linha["integrante_id"] for linha in linhas]
    finally:
        conn.close()
    return viagens


def criar(config: AppConfig, dados: dict) -> dict:
    viagem = _crud.criar(config, "viagem", _normalizar(dados))
    _salvar_passageiros(config, viagem["id"], dados.get("passageiros_ids") or [])
    webhook_service.disparar(config, "nova_viagem", viagem)
    return viagem


def atualizar(config: AppConfig, viagem_id: int, dados: dict) -> dict:
    viagem = _crud.atualizar(config, "viagem", viagem_id, _normalizar(dados))
    _salvar_passageiros(config, viagem_id, dados.get("passageiros_ids") or [])
    return viagem


def excluir(config: AppConfig, viagem_id: int) -> None:
    _crud.excluir(config, "viagem", viagem_id)
