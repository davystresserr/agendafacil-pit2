from datetime import datetime

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from ..models import Papel
from ..relogio import agora
from ..security import papel_obrigatorio
from ..services import agendamento_service, profissional_service
from ..services.erros import RegraNegocioError, ValidacaoError

bp = Blueprint("profissional", __name__, url_prefix="/profissional")


def _profissional():
    return g.usuario.profissional or abort(403)


@bp.get("/")
@papel_obrigatorio(Papel.PROFISSIONAL)
def painel():
    prof = _profissional()
    agora_ = agora()
    hoje = datetime.combine(agora_.date(), datetime.min.time())
    return render_template("profissional/painel.html", profissional=prof, agora_=agora_,
                           agendamentos=agendamento_service.do_profissional(prof, a_partir_de=hoje))


@bp.post("/horarios")
@papel_obrigatorio(Papel.PROFISSIONAL)
def adicionar_horario():
    f = request.form
    try:
        profissional_service.adicionar_horario(_profissional(), f.get("dia_semana"), f.get("hora_inicio"),
                                               f.get("hora_fim"))
        flash("Horário adicionado.", "sucesso")
    except ValidacaoError as e:
        for msg in e.erros.values():
            flash(msg, "erro")
    except RegraNegocioError as e:
        flash(str(e), "erro")
    return redirect(url_for("profissional.painel") + "#horarios")


@bp.post("/horarios/<int:horario_id>/remover")
@papel_obrigatorio(Papel.PROFISSIONAL)
def remover_horario(horario_id):
    try:
        profissional_service.remover_horario(_profissional(), horario_id)
        flash("Horário removido.", "sucesso")
    except RegraNegocioError as e:
        flash(str(e), "erro")
    return redirect(url_for("profissional.painel") + "#horarios")
