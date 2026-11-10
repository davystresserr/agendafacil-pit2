from datetime import date
from urllib.parse import urlencode

from flask import current_app

from .models.horario import DIAS_SEMANA
from .relogio import agora


def registrar_filtros(app):
    @app.template_filter("datahora")
    def datahora(valor):
        return valor.strftime("%d/%m/%Y %H:%M") if valor else ""

    @app.template_filter("data_br")
    def data_br(valor):
        return valor.strftime("%d/%m/%Y") if valor else ""

    @app.template_filter("hora")
    def hora(valor):
        return valor.strftime("%H:%M") if valor else ""

    @app.template_filter("dia_semana")
    def dia_semana(valor: date):
        return DIAS_SEMANA[valor.weekday()]

    @app.template_filter("google_agenda")
    def google_agenda(a):
        """Link que abre o Google Agenda com o evento já preenchido (sem API nem login no sistema)."""
        formato = "%Y%m%dT%H%M%S"
        return "https://calendar.google.com/calendar/render?" + urlencode({
            "action": "TEMPLATE",
            "text": f"{a.servico.nome} com {a.profissional.nome}",
            "dates": f"{a.inicio.strftime(formato)}/{a.fim.strftime(formato)}",
            "ctz": current_app.config["TZ_APP"],
            "details": f"Agendado pelo AgendaFácil.{' Observação: ' + a.observacao if a.observacao else ''}",
        })

    @app.context_processor
    def contexto():
        return {"agora": agora, "DIAS_SEMANA": DIAS_SEMANA}
