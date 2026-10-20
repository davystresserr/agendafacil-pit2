"""Verifica as restrições do PostgreSQL (EXCLUDE). Roda apenas se PG_TEST_URL estiver definida.

Exemplo: PG_TEST_URL=postgresql+psycopg://agendafacil:agendafacil@localhost:5432/agendafacil_teste pytest -m pg
"""
import os
from datetime import datetime

import pytest
import sqlalchemy as sa

PG_URL = os.environ.get("PG_TEST_URL")
pytestmark = [pytest.mark.pg, pytest.mark.skipif(not PG_URL, reason="PG_TEST_URL não definida")]


def test_exclude_impede_sobreposicao_no_banco():
    from alembic import command
    from alembic.config import Config as AlembicConfig

    from agendafacil import create_app
    from agendafacil.config import Config

    class PG(Config):
        SQLALCHEMY_DATABASE_URI = PG_URL.replace("postgresql://", "postgresql+psycopg://", 1) \
            if PG_URL.startswith("postgresql://") else PG_URL

    app = create_app(PG)
    with app.app_context():
        from agendafacil.extensions import db
        cfg = AlembicConfig(os.path.join(os.path.dirname(__file__), "..", "..", "src", "migrations", "alembic.ini"))
        cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "..", "..", "src", "migrations"))
        with db.engine.begin() as conn:
            conn.execute(sa.text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
        from flask_migrate import upgrade
        upgrade(directory=cfg.get_main_option("script_location"))
        with db.engine.begin() as conn:
            conn.execute(sa.text("INSERT INTO usuarios (nome,email,senha_hash) VALUES ('Cli','c@x.com','h'),"
                                 "('Pro','p@x.com','h')"))
            conn.execute(sa.text("INSERT INTO profissionais (usuario_id) VALUES (2)"))
            conn.execute(sa.text("INSERT INTO servicos (nome,preco,duracao_min) VALUES ('Corte',45,30)"))
            ins = sa.text("INSERT INTO agendamentos (cliente_id,profissional_id,servico_id,inicio,fim) "
                          "VALUES (1,1,1,:i,:f)")
            conn.execute(ins, {"i": datetime(2030, 1, 7, 10), "f": datetime(2030, 1, 7, 10, 30)})
        with pytest.raises(sa.exc.IntegrityError, match="ex_ag_sem_sobreposicao"):
            with db.engine.begin() as conn:
                conn.execute(ins, {"i": datetime(2030, 1, 7, 10, 15), "f": datetime(2030, 1, 7, 10, 45)})
        with db.engine.begin() as conn:  # intervalo encostado é permitido
            conn.execute(ins, {"i": datetime(2030, 1, 7, 10, 30), "f": datetime(2030, 1, 7, 11)})
        del command
