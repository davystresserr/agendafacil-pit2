from flask import flash, redirect, render_template, request, url_for

from ..extensions import db
from ..security import CSRFError, url_segura


def registrar_erros(app):
    @app.errorhandler(404)
    def nao_encontrado(e):
        return render_template("erros/404.html"), 404

    @app.errorhandler(403)
    def proibido(e):
        return render_template("erros/403.html"), 403

    @app.errorhandler(CSRFError)
    def csrf(e):
        flash("Sua sessão expirou. Recarregue a página e tente novamente.", "erro")
        destino = request.referrer if request.referrer and url_segura(_caminho(request.referrer)) else None
        return redirect(_caminho(destino) if destino else url_for("main.index"))

    @app.errorhandler(500)
    def erro_interno(e):
        db.session.rollback()
        app.logger.exception("Erro interno: %s", e)
        return render_template("erros/500.html"), 500

    @app.teardown_request
    def desfazer_transacao(exc):
        if exc is not None:
            db.session.rollback()


def _caminho(url):
    from urllib.parse import urlparse
    if not url:
        return None
    p = urlparse(url)
    return p.path + (f"?{p.query}" if p.query else "")
