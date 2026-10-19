from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from ..models import Papel
from ..security import encerrar_sessao, iniciar_sessao, url_segura
from ..services import auth_service
from ..services.erros import RegraNegocioError, ValidacaoError

bp = Blueprint("auth", __name__)


def destino_por_papel(usuario):
    if usuario.papel == Papel.ADMIN:
        return url_for("admin.painel")
    if usuario.papel == Papel.PROFISSIONAL:
        return url_for("profissional.painel")
    return url_for("main.index")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario:
        return redirect(destino_por_papel(g.usuario))
    if request.method == "POST":
        try:
            usuario = auth_service.autenticar(request.form.get("email"), request.form.get("senha"))
        except RegraNegocioError as e:
            flash(str(e), "erro")
            return render_template("auth/login.html", email=request.form.get("email", "")), 401
        iniciar_sessao(usuario)
        flash(f"Olá, {usuario.primeiro_nome}!", "sucesso")
        proximo = request.args.get("next")
        return redirect(proximo if url_segura(proximo) else destino_por_papel(usuario))
    return render_template("auth/login.html", email="")


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if g.usuario:
        return redirect(destino_por_papel(g.usuario))
    if request.method == "POST":
        f = request.form
        try:
            usuario = auth_service.cadastrar_cliente(f.get("nome"), f.get("email"), f.get("telefone"),
                                                     f.get("senha"), f.get("confirmacao"))
        except ValidacaoError as e:
            for msg in e.erros.values():
                flash(msg, "erro")
            return render_template("auth/cadastro.html", dados=f, erros=e.erros), 400
        iniciar_sessao(usuario)
        flash(f"Conta criada com sucesso! Bem-vindo(a), {usuario.primeiro_nome}.", "sucesso")
        return redirect(url_for("main.index"))
    return render_template("auth/cadastro.html", dados={}, erros={})


@bp.post("/logout")
def logout():
    encerrar_sessao()
    flash("Você saiu da sua conta.", "sucesso")
    return redirect(url_for("main.index"))
