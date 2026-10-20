"""Testes ponta a ponta (Playwright): agendar, cancelar e tentar agendar em horário ocupado."""
import re

import pytest
from playwright.sync_api import expect

from tests.e2e.conftest import proximo_dia_util

pytestmark = pytest.mark.e2e


def ir_para_horarios(page, servidor, servico="Corte masculino", profissional="Carlos", dia=None):
    dia = dia or proximo_dia_util()
    page.goto(f"{servidor}/")
    card = page.locator("[data-testid=servico]").filter(has=page.get_by_role("heading", name=servico, exact=True))
    card.get_by_role("link", name="Agendar").click()
    page.get_by_role("link", name=f"Escolher {profissional}").click()
    page.fill("#data", dia.isoformat())
    page.get_by_role("button", name="Ver horários").click()
    expect(page.get_by_role("heading", name=re.compile("Horários livres"))).to_be_visible()
    return dia


def test_e2e_agendar_horario(page, servidor, entrar):
    entrar()
    dia = ir_para_horarios(page, servidor)
    page.locator("label.horario", has_text="10:00").click()
    page.fill("#observacao", "Teste E2E agendar")
    page.get_by_role("button", name="Confirmar agendamento").click()

    expect(page).to_have_url(re.compile("/meus-agendamentos$"))
    expect(page.get_by_role("alert")).to_contain_text("Agendamento confirmado")
    linha = page.locator("[data-testid=agendamento]", has_text=f"{dia:%d/%m/%Y} 10:00")
    expect(linha).to_contain_text("Agendado")


def test_e2e_cancelar_agendamento(page, servidor, entrar):
    entrar()
    dia = ir_para_horarios(page, servidor, servico="Barba")
    page.locator("label.horario", has_text="15:00").click()
    page.get_by_role("button", name="Confirmar agendamento").click()
    linha = page.locator("[data-testid=agendamento]", has_text=f"{dia:%d/%m/%Y} 15:00")
    linha.get_by_role("button", name="Cancelar").click()

    dialogo = page.locator("dialog[open]")
    expect(dialogo).to_contain_text("O horário será liberado")
    dialogo.get_by_role("button", name="Sim, confirmar").click()

    expect(page.get_by_role("alert")).to_contain_text("Agendamento cancelado")
    expect(linha).to_contain_text("Cancelado")


def test_e2e_horario_ocupado(browser, servidor, entrar):
    """Dois clientes abrem o mesmo horário; o segundo a confirmar recebe a mensagem de horário ocupado."""
    ctx_a, ctx_b = browser.new_context(), browser.new_context()
    page_a, page_b = ctx_a.new_page(), ctx_b.new_page()
    try:
        # cria o segundo cliente pelo cadastro
        page_b.goto(f"{servidor}/cadastro")
        page_b.fill("#nome", "Bruno Segundo")
        page_b.fill("#email", "bruno.e2e@teste.com")
        page_b.fill("#senha", "senha-bruno-1")
        page_b.fill("#confirmacao", "senha-bruno-1")
        page_b.get_by_role("button", name="Criar conta").click()
        expect(page_b.get_by_role("alert")).to_contain_text("Conta criada")

        entrar(pagina=page_a)
        dia = ir_para_horarios(page_a, servidor, profissional="Ana", servico="Escova")
        ir_para_horarios(page_b, servidor, profissional="Ana", servico="Escova", dia=dia)

        page_a.locator("label.horario", has_text="14:00").click()
        page_b.locator("label.horario", has_text="14:00").click()
        page_a.get_by_role("button", name="Confirmar agendamento").click()
        expect(page_a.get_by_role("alert")).to_contain_text("Agendamento confirmado")

        page_b.get_by_role("button", name="Confirmar agendamento").click()
        expect(page_b.get_by_role("alert")).to_contain_text("acabou de ser ocupado")
        expect(page_b).to_have_url(re.compile("/agendar"))
        expect(page_b.locator("label.horario", has_text="14:00")).to_have_count(0)
    finally:
        ctx_a.close()
        ctx_b.close()
