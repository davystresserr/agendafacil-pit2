from flask import Blueprint, render_template

from ..services import servico_service

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return render_template("servicos.html", servicos=servico_service.listar_ativos())


@bp.get("/saude")
def saude():
    return {"status": "ok"}
