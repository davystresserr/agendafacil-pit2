"""Hora local do salão. Centralizado para facilitar testes."""
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import current_app


def agora() -> datetime:
    """Data/hora atual no fuso do salão, sem tzinfo (o banco guarda TIMESTAMP local)."""
    fuso = ZoneInfo(current_app.config.get("TZ_APP", "America/Sao_Paulo"))
    return datetime.now(fuso).replace(tzinfo=None, microsecond=0)
