from datetime import date
from urllib.parse import urlencode

from flask import current_app

from .models.horario import DIAS_SEMANA
from .relogio import agora


# Fotos do Unsplash (licença livre), escolhidas pelo tipo de serviço; créditos no README.
FOTOS = {
    "combo": "1647140655214-e4a2d914971f",      # Nate Johnston
    "feminino": "1700760934268-8aa0ef52ce0a",   # Farhad Ibrahimzade
    "escova": "1562322140-8baeececf3df",        # Adam Winger
    "barba": "1599011176306-4a96f1516d4d",      # Mr Shave
    "masculino": "1593702275687-f8b402bf1fb5",  # Michael DeMoya
    "geral": "1503951914875-452162b0f3f1",      # Allef Vinicius
}


def foto_servico(nome: str) -> str:
    n = (nome or "").lower()
    if "barba" in n and ("corte" in n or "combo" in n):
        tipo = "combo"
    elif "feminino" in n:
        tipo = "feminino"
    elif "escova" in n:
        tipo = "escova"
    elif "barba" in n:
        tipo = "barba"
    elif "corte" in n or "masculino" in n:
        tipo = "masculino"
    else:  # serviço novo cadastrado pelo admin
        tipo = "geral"
    return f"https://images.unsplash.com/photo-{FOTOS[tipo]}?w=480&h=360&fit=crop&auto=format&q=70"


def registrar_filtros(app):
    app.add_template_filter(foto_servico, "foto_servico")

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
