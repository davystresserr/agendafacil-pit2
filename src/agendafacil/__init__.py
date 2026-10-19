"""AgendaFácil: sistema web de agendamento para salões e barbearias (Flask, MVC)."""
import logging
import os

from flask import Flask

from .config import Config, ProductionConfig
from .extensions import db, migrate

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app(config_object=None):
    app = Flask(__name__)
    if config_object is None:
        config_object = ProductionConfig if os.environ.get("FLASK_ENV") == "production" else Config
    app.config.from_object(config_object)

    if config_object is ProductionConfig and app.config["SECRET_KEY"] == "dev-inseguro-troque":
        raise RuntimeError("Defina a variável SECRET_KEY em produção.")

    db.init_app(app)
    migrate.init_app(app, db, directory=os.path.join(os.path.dirname(BASE_DIR), "migrations"))

    from . import models  # noqa: F401  (registra as tabelas no metadata)
    from .controllers import registrar_blueprints
    from .controllers.erros import registrar_erros
    from .security import carregar_usuario, csrf_token, verificar_csrf
    from .filtros import registrar_filtros

    app.before_request(carregar_usuario)
    app.before_request(verificar_csrf)
    app.jinja_env.globals["csrf_token"] = csrf_token
    registrar_filtros(app)
    registrar_blueprints(app)
    registrar_erros(app)

    from .cli import registrar_cli
    registrar_cli(app)

    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)
    return app
