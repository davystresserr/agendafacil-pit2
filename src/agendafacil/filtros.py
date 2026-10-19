from datetime import date

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

    @app.context_processor
    def contexto():
        return {"agora": agora, "DIAS_SEMANA": DIAS_SEMANA}
