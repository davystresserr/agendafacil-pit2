from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..extensions import db
from ..models import Papel, Servico
from ..relogio import agora
from ..security import papel_obrigatorio
from ..services import agendamento_service, profissional_service, servico_service
from ..services.erros import ValidacaoError

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/")
@papel_obrigatorio(Papel.ADMIN)
def painel():
    return render_template(
        "admin/painel.html", servicos=servico_service.listar_todos(),
        profissionais=profissional_service.listar_todos(),
        agendamentos_hoje=agendamento_service.contar_do_dia(agora().date()),
    )


@bp.route("/servicos/novo", methods=["GET", "POST"])
@papel_obrigatorio(Papel.ADMIN)
def novo_servico():
    if request.method == "POST":
        f = request.form
        try:
            servico_service.criar(f.get("nome"), f.get("preco"), f.get("duracao_min"), f.get("descricao"))
        except ValidacaoError as e:
            for msg in e.erros.values():
                flash(msg, "erro")
            return render_template("admin/servico_form.html", servico=None, dados=f, erros=e.erros), 400
        flash("Serviço salvo com sucesso.", "sucesso")
        return redirect(url_for("admin.painel"))
    return render_template("admin/servico_form.html", servico=None, dados={}, erros={})


@bp.route("/servicos/<int:servico_id>/editar", methods=["GET", "POST"])
@papel_obrigatorio(Papel.ADMIN)
def editar_servico(servico_id):
    servico = db.session.get(Servico, servico_id) or abort(404)
    if request.method == "POST":
        f = request.form
        try:
            servico_service.atualizar(servico, f.get("nome"), f.get("preco"), f.get("duracao_min"),
                                      f.get("descricao"))
        except ValidacaoError as e:
            db.session.rollback()
            for msg in e.erros.values():
                flash(msg, "erro")
            return render_template("admin/servico_form.html", servico=servico, dados=f, erros=e.erros), 400
        flash("Serviço salvo com sucesso.", "sucesso")
        return redirect(url_for("admin.painel"))
    dados = {"nome": servico.nome, "preco": f"{servico.preco:.2f}".replace(".", ","),
             "duracao_min": servico.duracao_min, "descricao": servico.descricao or ""}
    return render_template("admin/servico_form.html", servico=servico, dados=dados, erros={})


@bp.post("/servicos/<int:servico_id>/alternar")
@papel_obrigatorio(Papel.ADMIN)
def alternar_servico(servico_id):
    servico = db.session.get(Servico, servico_id) or abort(404)
    servico_service.alternar_ativo(servico)
    flash(f"Serviço {'ativado' if servico.ativo else 'desativado'}.", "sucesso")
    return redirect(url_for("admin.painel"))


@bp.route("/profissionais", methods=["GET", "POST"])
@papel_obrigatorio(Papel.ADMIN)
def profissionais():
    dados, erros, status = {}, {}, 200
    if request.method == "POST":
        f = request.form
        try:
            prof = profissional_service.cadastrar(f.get("nome"), f.get("email"), f.get("senha"),
                                                  f.get("especialidade"), f.get("bio"), f.getlist("servicos"))
            flash(f"Profissional {prof.nome} cadastrado.", "sucesso")
            return redirect(url_for("admin.profissionais"))
        except ValidacaoError as e:
            db.session.rollback()
            for msg in e.erros.values():
                flash(msg, "erro")
            dados, erros, status = f, e.erros, 400
    return render_template("admin/profissionais.html", profissionais=profissional_service.listar_todos(),
                           servicos=servico_service.listar_ativos(), dados=dados, erros=erros), status


@bp.get("/agendamentos")
@papel_obrigatorio(Papel.ADMIN)
def agendamentos():
    return render_template("admin/agendamentos.html", agendamentos=agendamento_service.todos(), agora_=agora())
