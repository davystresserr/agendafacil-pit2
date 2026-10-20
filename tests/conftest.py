from datetime import datetime, time
from decimal import Decimal

import pytest

from agendafacil import create_app
from agendafacil.config import TestConfig
from agendafacil.extensions import db as _db
from agendafacil.models import HorarioDisponivel, Papel, Profissional, Servico, Usuario

# Segunda-feira, 19/10/2026, 08:00 — "agora" fixo dos testes unitários e de integração
AGORA = datetime(2026, 10, 19, 8, 0)
SENHA = "senha-teste-123"


class Config(TestConfig):
    AGORA_FIXO = AGORA


@pytest.fixture
def app():
    app = create_app(Config)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def client(app):
    return app.test_client()


def criar_usuario(nome, email, papel=Papel.CLIENTE):
    u = Usuario(nome=nome, email=email, papel=papel, telefone="(43) 99999-0000")
    u.definir_senha(SENHA)
    _db.session.add(u)
    _db.session.commit()
    return u


@pytest.fixture
def dados(db):
    """Cenário base: 2 serviços, 1 profissional (seg–sáb 9–12 e 13–18), 1 cliente, 1 admin."""
    corte = Servico(nome="Corte masculino", preco=Decimal("45.00"), duracao_min=30)
    barba = Servico(nome="Barba", preco=Decimal("30.00"), duracao_min=60)
    escova = Servico(nome="Escova", preco=Decimal("60.00"), duracao_min=45)
    db.session.add_all([corte, barba, escova])
    cliente = criar_usuario("Ana Cliente", "ana@teste.com")
    admin = criar_usuario("Admin Geral", "admin@teste.com", Papel.ADMIN)
    u_prof = criar_usuario("Carlos Barbeiro", "carlos@teste.com", Papel.PROFISSIONAL)
    prof = Profissional(usuario=u_prof, especialidade="Barbeiro", servicos=[corte, barba])
    for dia in range(6):
        prof.horarios.append(HorarioDisponivel(dia_semana=dia, hora_inicio=time(9), hora_fim=time(12)))
        prof.horarios.append(HorarioDisponivel(dia_semana=dia, hora_inicio=time(13), hora_fim=time(18)))
    db.session.add(prof)
    db.session.commit()
    return {"corte": corte, "barba": barba, "escova": escova, "cliente": cliente, "admin": admin,
            "profissional": prof, "u_prof": u_prof}


def login(client, email, senha=SENHA):
    return client.post("/login", data={"email": email, "senha": senha}, follow_redirects=True)
