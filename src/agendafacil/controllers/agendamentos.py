from calendar import Calendar
from datetime import date, datetime, timedelta

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for

from ..extensions import db
from ..models import Agendamento, Papel, Profissional, Servico
from ..relogio import agora
from ..security import LINKS_SESSAO, login_obrigatorio, papel_obrigatorio
from ..services import agendamento_service, profissional_service, servico_service
from ..services.erros import RegraNegocioError
from ..services.validacao import converter_data, converter_datahora, converter_int

bp = Blueprint("agendamentos", __name__)
LINKS_MAX = 20  # agendamentos sem conta lembrados neste aparelho (cookie de sessão)


MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro",
         "novembro", "dezembro"]


def _calendario(profissional, ref: date, data_min: date, data_max: date) -> dict:
    """Mês no formato do Google Agenda (semana começando no domingo); só dias de expediente são clicáveis."""
    primeiro = ref.replace(day=1)
    expediente = {h.dia_semana for h in profissional.horarios}
    anterior = (primeiro - timedelta(days=1)).replace(day=1)
    proximo = (primeiro + timedelta(days=32)).replace(day=1)
    return {
        "titulo": f"{MESES[primeiro.month - 1]} de {primeiro.year}",
        "mes": primeiro.month,
        "semanas": Calendar(firstweekday=6).monthdatescalendar(primeiro.year, primeiro.month),
        "disponivel": lambda d: data_min <= d <= data_max and d.weekday() in expediente,
        "anterior": anterior if anterior >= data_min.replace(day=1) else None,
        "proximo": proximo if proximo <= data_max else None,
    }


def _mes(valor) -> date | None:
    try:
        return datetime.strptime(valor or "", "%Y-%m").date()
    except ValueError:
        return None


def _so_cliente_ou_visitante():
    if g.usuario is not None and not g.usuario.is_cliente:
        abort(403)


def _obter(modelo, valor, somente_ativo=True):
    obj = db.session.get(modelo, converter_int(valor) or 0)
    if obj is None or (somente_ativo and not obj.ativo):
        return None
    return obj


@bp.get("/agendar")
def agendar():
    _so_cliente_ou_visitante()
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
    horarios = (agendamento_service.horarios_do_dia(profissional, servico, data, agora_)
                if servico and profissional and data else [])
    passo = 1 if not servico else 2 if not profissional else 3
    data_min, data_max = agora_.date(), agora_.date() + timedelta(days=60)
    calendario = (_calendario(profissional, data or _mes(request.args.get("mes")) or data_min, data_min, data_max)
                  if servico and profissional else None)
    return render_template(
        "agendamentos/agendar.html", servicos=servico_service.listar_ativos(), servico=servico,
        profissionais=profissionais, profissional=profissional, data=data, horarios=horarios, passo=passo,
        calendario=calendario, hoje=data_min,
    )


@bp.post("/agendar")
def confirmar():
    _so_cliente_ou_visitante()
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
        if g.usuario:
            ag = agendamento_service.agendar(g.usuario, profissional, servico, inicio, agora(), f.get("observacao"))
        else:
            ag = agendamento_service.agendar_sem_conta(f.get("nome"), f.get("telefone"), profissional, servico,
                                                       inicio, agora(), f.get("observacao"))
    except RegraNegocioError as e:
        flash(str(e), "erro")
        return redirect(voltar)
    flash(f"Agendamento confirmado: {servico.nome} com {profissional.nome} em "
          f"{ag.inicio:%d/%m/%Y} às {ag.inicio:%H:%M}.", "sucesso")
    if g.usuario:
        return redirect(url_for("agendamentos.meus"))
    session.permanent = True  # lembra o agendamento neste aparelho por 31 dias
    session[LINKS_SESSAO] = ([ag.token] + session.get(LINKS_SESSAO, []))[:LINKS_MAX]
    return redirect(url_for("agendamentos.pelo_link", token=ag.token))


@bp.get("/meus-agendamentos")
def meus():
    _so_cliente_ou_visitante()
    if g.usuario:
        agendamentos = agendamento_service.do_cliente(g.usuario)
    else:
        agendamentos = agendamento_service.pelos_tokens(session.get(LINKS_SESSAO, []))
    return render_template("agendamentos/meus.html", agendamentos=agendamentos, agora_=agora())


@bp.get("/a/<token>")
def pelo_link(token):
    ag = agendamento_service.pelo_token(token) or abort(404)
    return render_template("agendamentos/link.html", a=ag, agora_=agora())


@bp.post("/a/<token>/cancelar")
def cancelar_pelo_link(token):
    ag = agendamento_service.pelo_token(token) or abort(404)
    try:
        agendamento_service.cancelar_pelo_link(ag, agora())
        flash("Agendamento cancelado. O horário foi liberado.", "sucesso")
    except RegraNegocioError as e:
        flash(str(e), "erro")
    return redirect(url_for("agendamentos.pelo_link", token=token))


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
