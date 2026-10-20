"""Gera prints das telas principais em docs/evidencias/ usando Playwright.

Uso: python scripts/gerar_evidencias.py
Sobe a aplicação em uma thread com um banco SQLite temporário e dados de demonstração.
"""
import sys
import tempfile
import threading
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from playwright.sync_api import sync_playwright  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

from agendafacil import create_app  # noqa: E402
from agendafacil.cli import popular  # noqa: E402
from agendafacil.config import TestConfig  # noqa: E402
from agendafacil.extensions import db  # noqa: E402

SAIDA = RAIZ / "docs" / "evidencias"
SENHA = "senha-demo-123"


def proximo_dia_util():
    d = date.today() + timedelta(days=2)
    while d.weekday() == 6:
        d += timedelta(days=1)
    return d


def subir_servidor():
    banco = Path(tempfile.mkdtemp()) / "evidencias.db"

    class Cfg(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{banco}"
        WTF_CSRF_ENABLED = True

    app = create_app(Cfg)
    with app.app_context():
        db.create_all()
        popular(SENHA)
    srv = make_server("127.0.0.1", 0, app, threaded=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_port}"


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    srv, url = subir_servidor()
    dia = proximo_dia_util()

    def foto(page, nome, full=True):
        page.screenshot(path=str(SAIDA / f"{nome}.png"), full_page=full)
        print("print:", nome)

    def entrar(page, email):
        page.goto(f"{url}/login")
        page.fill("#email", email)
        page.fill("#senha", SENHA)
        page.click("button:has-text('Entrar')")

    with sync_playwright() as p:
        nav = p.chromium.launch()
        ctx = nav.new_context(viewport={"width": 1280, "height": 800}, locale="pt-BR")
        page = ctx.new_page()

        page.goto(url)
        foto(page, "01-lista-servicos")
        page.goto(f"{url}/login")
        foto(page, "02-login")
        page.fill("#email", "cliente@agendafacil.com")
        page.fill("#senha", "errada")
        page.click("button:has-text('Entrar')")
        foto(page, "03-login-erro")

        page.goto(f"{url}/cadastro")
        page.fill("#nome", "Teste Validação")
        page.fill("#email", "cliente@agendafacil.com")
        page.fill("#senha", "12345678")
        page.fill("#confirmacao", "1234567")
        page.locator("#confirmacao").dispatch_event("input")
        foto(page, "04-cadastro-validacao-cliente")
        page.fill("#confirmacao", "12345678")
        page.click("button:has-text('Criar conta')")
        foto(page, "05-cadastro-email-duplicado")

        entrar(page, "cliente@agendafacil.com")
        page.goto(f"{url}/agendar")
        foto(page, "06-agendar-passo1-servico")
        page.goto(f"{url}/agendar?servico_id=1")
        foto(page, "07-agendar-passo2-profissional")
        page.goto(f"{url}/agendar?servico_id=1&profissional_id=1&data={dia.isoformat()}")
        page.locator("label.horario", has_text="10:00").click()
        foto(page, "08-agendar-passo3-horarios")
        page.click("button:has-text('Confirmar agendamento')")
        foto(page, "09-agendamento-confirmado")

        page.goto(f"{url}/agendar?servico_id=1&profissional_id=1&data={dia.isoformat()}")
        page.locator("label.horario", has_text="14:00").click()
        page.click("button:has-text('Confirmar agendamento')")
        page.locator("[data-testid=agendamento]", has_text="14:00").get_by_role("button", name="Cancelar").click()
        page.wait_for_selector("dialog[open]")
        foto(page, "10-cancelar-confirmacao", full=False)
        page.click("dialog[open] >> text=Sim, confirmar")
        foto(page, "11-agendamento-cancelado")

        # horário ocupado: segundo navegador tenta o mesmo horário (10:00) já reservado
        ctx2 = nav.new_context(viewport={"width": 1280, "height": 800})
        p2 = ctx2.new_page()
        p2.goto(f"{url}/cadastro")
        p2.fill("#nome", "Bruno Demonstração")
        p2.fill("#email", "bruno@demo.com")
        p2.fill("#senha", "12345678")
        p2.fill("#confirmacao", "12345678")
        p2.click("button:has-text('Criar conta')")
        p2.goto(f"{url}/agendar?servico_id=1&profissional_id=1&data={dia.isoformat()}")
        p2.evaluate("""inicio => {
            const f = document.querySelector('form[method=post][action$="/agendar"]');
            const r = f.querySelector('input[name=inicio]'); r.value = inicio; r.checked = true;
            f.submit(); }""", f"{dia.isoformat()}T10:00")
        p2.wait_for_load_state()
        foto(p2, "12-horario-ocupado")
        ctx2.close()

        page.goto(f"{url}/nao-existe")
        foto(page, "13-pagina-404")
        page.goto(f"{url}/admin/")
        foto(page, "14-acesso-negado-403")

        page.click("button:has-text('Sair')")
        entrar(page, "carlos@agendafacil.com")
        foto(page, "15-painel-profissional")

        page.click("button:has-text('Sair')")
        entrar(page, "admin@agendafacil.com")
        foto(page, "16-painel-admin")
        page.goto(f"{url}/admin/servicos/novo")
        page.fill("#nome", "Serviço inválido")
        page.fill("#preco", "0")
        page.fill("#duracao_min", "1000")
        page.evaluate("document.querySelector('form').noValidate = true; document.querySelector('form').removeAttribute('data-validar')")
        page.evaluate("document.querySelector('form').submit()")
        page.wait_for_load_state()
        foto(page, "17-admin-servico-invalido")
        page.goto(f"{url}/admin/profissionais")
        foto(page, "18-admin-profissionais")
        page.goto(f"{url}/admin/agendamentos")
        foto(page, "19-admin-agendamentos")

        mob = nav.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True)
        m = mob.new_page()
        m.goto(url)
        foto(m, "20-mobile-servicos")
        m.goto(f"{url}/login")
        m.fill("#email", "cliente@agendafacil.com")
        m.fill("#senha", SENHA)
        m.click("button:has-text('Entrar')")
        m.goto(f"{url}/meus-agendamentos")
        foto(m, "21-mobile-meus-agendamentos")
        m.click("[data-menu]")
        foto(m, "22-mobile-menu", full=False)
        nav.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
