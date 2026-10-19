"""Comandos de linha: flask seed (dados de demonstração)."""
import os
import secrets
from datetime import time
from decimal import Decimal

import click

from .extensions import db
from .models import HorarioDisponivel, Papel, Profissional, Servico, Usuario

SERVICOS = [
    ("Corte masculino", "Corte na tesoura ou máquina, com acabamento.", Decimal("45.00"), 30),
    ("Barba", "Barba modelada com toalha quente.", Decimal("30.00"), 30),
    ("Corte + barba", "Combo completo.", Decimal("70.00"), 60),
    ("Escova", "Escova modeladora.", Decimal("60.00"), 45),
    ("Corte feminino", "Corte com lavagem e finalização.", Decimal("80.00"), 60),
]

PROFISSIONAIS = [
    ("Carlos Barbeiro", "carlos@agendafacil.com", "Barbeiro", ["Corte masculino", "Barba", "Corte + barba"]),
    ("Ana Cabeleireira", "ana@agendafacil.com", "Cabeleireira", ["Escova", "Corte feminino", "Corte masculino"]),
]


def _usuario(nome, email, papel, senha):
    u = Usuario.query.filter_by(email=email).first()
    if u is None:
        u = Usuario(nome=nome, email=email, papel=papel)
        u.definir_senha(senha)
        db.session.add(u)
    return u


def popular(senha: str):
    """Cria dados de demonstração. Idempotente: não duplica se já existirem."""
    servicos = {}
    for nome, desc, preco, dur in SERVICOS:
        s = Servico.query.filter_by(nome=nome).first() or Servico(nome=nome, descricao=desc, preco=preco,
                                                                 duracao_min=dur)
        db.session.add(s)
        servicos[nome] = s

    _usuario("Administrador", "admin@agendafacil.com", Papel.ADMIN, senha)
    _usuario("Cliente Demonstração", "cliente@agendafacil.com", Papel.CLIENTE, senha)

    for nome, email, esp, nomes_serv in PROFISSIONAIS:
        u = _usuario(nome, email, Papel.PROFISSIONAL, senha)
        if u.profissional is None:
            p = Profissional(usuario=u, especialidade=esp, servicos=[servicos[n] for n in nomes_serv])
            for dia in range(0, 6):  # segunda a sábado
                p.horarios.append(HorarioDisponivel(dia_semana=dia, hora_inicio=time(9), hora_fim=time(12)))
                p.horarios.append(HorarioDisponivel(dia_semana=dia, hora_inicio=time(13), hora_fim=time(19)))
            db.session.add(p)
    db.session.commit()


def registrar_cli(app):
    @app.cli.command("seed")
    def seed():
        """Popula o banco com serviços, profissionais e usuários de demonstração."""
        senha = os.environ.get("SEED_PASSWORD")
        gerada = False
        if not senha:
            senha, gerada = secrets.token_urlsafe(9), True
        popular(senha)
        click.echo("Dados de demonstração criados (admin@, carlos@, ana@, cliente@agendafacil.com).")
        if gerada:
            click.echo(f"SEED_PASSWORD não definida. Senha gerada para os usuários novos: {senha}")
