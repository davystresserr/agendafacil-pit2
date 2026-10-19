from datetime import timedelta

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from ..extensions import db
from ..models import Agendamento, Papel, Profissional, Servico
from ..relogio import agora
from ..security import login_obrigatorio, papel_obrigatorio
from ..services import agendamento_service, profissional_service, servico_service
from ..services.erros import RegraNegocioError
from ..services.validacao import converter_data, converter_datahora, converter_int

bp = Blueprint("agendamentos", __name__)


def _obter(modelo, valor, somente_ativo=True):
    obj = db.session.get(modelo, converter_int(valor) or 0)
    if obj is None or (somente_ativo and not obj.ativo):
        return None
    return obj


@bp.get("/agendar")
@papel_obrigatorio(Papel.CLIENTE)
def agendar():
    agora_ = agora()
    servico = _obter(Servico, request.args.get("servico_id"))
    profissional = _obter(Profissional, request.args.get("profissional_id"))
    data = converter_data(request.args.get("data"))

    profissionais = profissional_service.que_realizam(servico) if servico else []
    if profissional and servico and not profissional.realiza(servico):
        profissional = None
    if data and data < agora_.date():
        flash("Escolha uma data a partir de hoje.", "aviso")
        data = None
    horarios = (agendamento_service.horarios_livres(profissional, servico, data, agora_)
                if servico and profissional and data else [])
    passo = 1 if not servico else 2 if not profissional else 3
    return render_template(
        "agendamentos/agendar.html", servicos=servico_service.listar_ativos(), servico=servico,
        profissionais=profissionais, profissional=profissional, data=data, horarios=horarios, passo=passo,
        data_min=agora_.date().isoformat(), data_max=(agora_.date() + timedelta(days=60)).isoformat(),
    )


@bp.post("/agendar")
@papel_obrigatorio(Papel.CLIENTE)
def confirmar():
    f = request.form
    servico = _obter(Servico, f.get("servico_id"))
    profissional = _obter(Profissional, f.get("profissional_id"))
    inicio = converter_datahora(f.get("inicio"))
    voltar = url_for("agendamentos.agendar", servico_id=f.get("servico_id"),
                     profissional_id=f.get("profissional_id"), data=inicio.date().isoformat() if inicio else None)
    if not (servico and profissional and inicio):
        flash("Escolha serviço, profissional e horário.", "erro")
        return redirect(voltar)
    try:
        ag = agendamento_service.agendar(g.usuario, profissional, servico, inicio, agora(), f.get("observacao"))
    except RegraNegocioError as e:
        flash(str(e), "erro")
        return redirect(voltar)
    flash(f"Agendamento confirmado: {servico.nome} com {profissional.nome} em "
          f"{ag.inicio:%d/%m/%Y} às {ag.inicio:%H:%M}.", "sucesso")
    return redirect(url_for("agendamentos.meus"))


@bp.get("/meus-agendamentos")
@papel_obrigatorio(Papel.CLIENTE)
def meus():
    return render_template("agendamentos/meus.html", agendamentos=agendamento_service.do_cliente(g.usuario),
                           agora_=agora())


@bp.post("/agendamentos/<int:agendamento_id>/cancelar")
@login_obrigatorio
def cancelar(agendamento_id):
    ag = db.session.get(Agendamento, agendamento_id) or abort(404)
    try:
        agendamento_service.cancelar(ag, g.usuario, agora())
        flash("Agendamento cancelado. O horário foi liberado.", "sucesso")
    except RegraNegocioError as e:
        flash(str(e), "erro")
    return redirect(_voltar_para())


@bp.post("/agendamentos/<int:agendamento_id>/concluir")
@papel_obrigatorio(Papel.PROFISSIONAL, Papel.ADMIN)
def concluir(agendamento_id):
    ag = db.session.get(Agendamento, agendamento_id) or abort(404)
    try:
        agendamento_service.concluir(ag, g.usuario, agora())
        flash("Atendimento marcado como concluído.", "sucesso")
    except RegraNegocioError as e:
        flash(str(e), "erro")
    return redirect(_voltar_para())


def _voltar_para():
    if g.usuario.is_admin:
        return url_for("admin.agendamentos")
    if g.usuario.is_profissional:
        return url_for("profissional.painel")
    return url_for("agendamentos.meus")
