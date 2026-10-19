"""Sessão, controle de acesso por papel e proteção CSRF."""
import hmac
import secrets
from functools import wraps
from urllib.parse import urlparse

from flask import abort, current_app, flash, g, redirect, request, session, url_for

from .extensions import db
from .models import Usuario

CSRF_CAMPO = "csrf_token"


class CSRFError(Exception):
    pass


def csrf_token() -> str:
    if CSRF_CAMPO not in session:
        session[CSRF_CAMPO] = secrets.token_urlsafe(32)
    return session[CSRF_CAMPO]


def verificar_csrf():
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return
    if not current_app.config.get("WTF_CSRF_ENABLED", True):
        return
    enviado = request.form.get(CSRF_CAMPO, "")
    esperado = session.get(CSRF_CAMPO, "")
    if not esperado or not hmac.compare_digest(enviado, esperado):
        raise CSRFError()


def carregar_usuario():
    g.usuario = None
    uid = session.get("usuario_id")
    if uid is not None:
        usuario = db.session.get(Usuario, uid)
        if usuario is not None and usuario.ativo:
            g.usuario = usuario
        else:
            session.pop("usuario_id", None)


def iniciar_sessao(usuario: Usuario):
    session.clear()  # evita fixação de sessão
    session["usuario_id"] = usuario.id
    csrf_token()


def encerrar_sessao():
    session.clear()


def url_segura(destino: str | None) -> bool:
    if not destino:
        return False
    partes = urlparse(destino)
    return not partes.scheme and not partes.netloc and destino.startswith("/") and not destino.startswith("//")


def login_obrigatorio(view):
    @wraps(view)
    def envolvida(*args, **kwargs):
        if g.get("usuario") is None:
            flash("Faça login para continuar.", "aviso")
            return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
        return view(*args, **kwargs)
    return envolvida


def papel_obrigatorio(*papeis):
    def decorador(view):
        @wraps(view)
        @login_obrigatorio
        def envolvida(*args, **kwargs):
            if g.usuario.papel not in papeis:
                abort(403)
            return view(*args, **kwargs)
        return envolvida
    return decorador
