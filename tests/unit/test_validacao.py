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
