from datetime import date, datetime, time
from decimal import Decimal

import pytest

from agendafacil.services import validacao as v


@pytest.mark.parametrize("entrada, esperado", [("45,00", Decimal("45.00")), ("1.234,5", Decimal("1234.50")),
                                               ("R$ 30", Decimal("30.00")), ("19.9", Decimal("19.90"))])
def test_preco_aceita_formatos_brasileiros(entrada, esperado):
    erros = {}
    assert v.validar_preco(entrada, erros) == esperado and not erros


@pytest.mark.parametrize("entrada", ["abc", "0", "-5", "", "99999999"])
def test_preco_invalido(entrada):
    erros = {}
    v.validar_preco(entrada, erros)
    assert "preco" in erros


@pytest.mark.parametrize("entrada, ok", [("30", True), ("5", True), ("480", True), ("4", False), ("481", False), ("x", False)])
def test_duracao(entrada, ok):
    erros = {}
    v.validar_duracao(entrada, erros)
    assert ("duracao_min" not in erros) is ok


def test_email_normalizado_e_validado():
    erros = {}
    assert v.validar_email("  Ana@Teste.COM ", erros) == "ana@teste.com" and not erros
    v.validar_email("sem-arroba", erros)
    assert "email" in erros
    erros = {}
    v.validar_email("", erros)
    assert erros["email"].startswith("Preencha")


def test_nome_telefone_senha():
    erros = {}
    v.validar_nome("A", erros)
    v.validar_telefone("abc", erros)
    v.validar_senha("curta", None, erros)
    assert set(erros) == {"nome", "telefone", "senha"}
    erros = {}
    v.validar_nome("", erros)
    assert v.validar_telefone("", erros) is None
    v.validar_senha("12345678", "87654321", erros)
    assert set(erros) == {"nome", "confirmacao"}


def test_conversores():
    assert v.converter_data("2026-10-20") == date(2026, 10, 20)
    assert v.converter_data("20/10/2026") is None
    assert v.converter_hora("09:30") == time(9, 30)
    assert v.converter_hora(None) is None
    assert v.converter_datahora("2026-10-20T10:00") == datetime(2026, 10, 20, 10, 0)
    assert v.converter_datahora("ontem") is None
    assert v.converter_int("7") == 7 and v.converter_int("x") is None


@pytest.mark.parametrize("entrada", ["((((((((", "--------", "+++ +++ ++", "( ) - ( ) -", "1234567", "123456789012"])
def test_telefone_sem_digitos_suficientes_e_recusado(entrada):
    # C-01: antes, um telefone só com símbolos passava na validação
    erros = {}
    v.validar_telefone(entrada, erros)
    assert "telefone" in erros


@pytest.mark.parametrize("entrada, esperado", [
    ("43999991111", "(43) 99999-1111"),
    ("(43) 99999-1111", "(43) 99999-1111"),
    ("43 3333-4444", "(43) 3333-4444"),
    ("+55 43 99999-1111", "(43) 99999-1111"),
])
def test_telefone_valido_e_formatado(entrada, esperado):
    erros = {}
    assert v.validar_telefone(entrada, erros) == esperado and not erros


@pytest.mark.parametrize("nome, foto", [
    ("Corte + barba", "1647140655214"), ("Corte feminino", "1700760934268"), ("Escova", "1562322140"),
    ("Barba", "1599011176306"), ("Corte masculino", "1593702275687"), ("Hidratação", "1503951914875"),
])
def test_foto_do_servico_pelo_nome(nome, foto):
    from agendafacil.filtros import foto_servico
    assert foto in foto_servico(nome) and foto_servico(nome).startswith("https://images.unsplash.com/")
