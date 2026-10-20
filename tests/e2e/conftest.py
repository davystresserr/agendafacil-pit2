"""Servidor real (thread) + banco SQLite em arquivo para os testes ponta a ponta."""
import threading
from datetime import date, timedelta

import pytest
from werkzeug.serving import make_server

from agendafacil import create_app
from agendafacil.cli import popular
from agendafacil.config import TestConfig
from agendafacil.extensions import db

SENHA_E2E = "senha-e2e-123"


def proximo_dia_util(minimo_dias=2) -> date:
    d = date.today() + timedelta(days=minimo_dias)
    while d.weekday() == 6:  # domingo não tem expediente no seed
        d += timedelta(days=1)
    return d


@pytest.fixture(scope="session")
def servidor(tmp_path_factory):
    caminho = tmp_path_factory.mktemp("e2e") / "e2e.db"

    class E2EConfig(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{caminho}"
        WTF_CSRF_ENABLED = True

    app = create_app(E2EConfig)
    with app.app_context():
        db.create_all()
        popular(SENHA_E2E)
    srv = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


@pytest.fixture
def entrar(page, servidor):
    def _entrar(email="cliente@agendafacil.com", pagina=None):
        p = pagina or page
        p.goto(f"{servidor}/login")
        p.fill("#email", email)
        p.fill("#senha", SENHA_E2E)
        p.click("button:has-text('Entrar')")
        return p
    return _entrar
