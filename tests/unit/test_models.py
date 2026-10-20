from datetime import datetime, time, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from agendafacil.models import Agendamento, HorarioDisponivel, Servico, StatusAgendamento, Usuario
from tests.conftest import AGORA


def test_senha_e_armazenada_como_hash(db):
    u = Usuario(nome="Teste", email="t@t.com")
    u.definir_senha("minha-senha")
    assert u.senha_hash != "minha-senha"
    assert u.verificar_senha("minha-senha")
    assert not u.verificar_senha("errada")


def test_papeis_e_primeiro_nome():
    u = Usuario(nome="Maria da Silva", email="m@m.com", papel="admin")
    assert u.is_admin and not u.is_cliente and not u.is_profissional
    assert u.primeiro_nome == "Maria"
    assert "admin" in repr(u)


def test_preco_formatado_em_reais():
    assert Servico(nome="X", preco=Decimal("1234.5"), duracao_min=10).preco_formatado == "R$ 1.234,50"


def test_horario_contem_intervalo():
    h = HorarioDisponivel(dia_semana=0, hora_inicio=time(9), hora_fim=time(12))
    seg = datetime(2026, 10, 19, 11, 30)
    assert h.contem(seg, seg + timedelta(minutes=30))
    assert not h.contem(seg, seg + timedelta(minutes=31))           # passa do fim
    assert not h.contem(seg + timedelta(days=1), seg + timedelta(days=1, minutes=30))  # terça
    assert h.dia_nome == "Segunda"


@pytest.mark.parametrize("antecedencia, esperado", [(timedelta(hours=2), True), (timedelta(hours=1, minutes=59), False)])
def test_regra_de_cancelamento_2_horas(antecedencia, esperado):
    a = Agendamento(inicio=AGORA + antecedencia, fim=AGORA + antecedencia + timedelta(minutes=30),
                    status=StatusAgendamento.AGENDADO)
    assert a.pode_ser_cancelado_por_cliente(AGORA) is esperado


def test_agendamento_cancelado_nao_pode_ser_cancelado_de_novo():
    a = Agendamento(inicio=AGORA + timedelta(days=1), fim=AGORA + timedelta(days=1, hours=1),
                    status=StatusAgendamento.CANCELADO)
    assert not a.pode_ser_cancelado_por_cliente(AGORA)
    assert a.status_rotulo == "Cancelado"


def test_banco_rejeita_email_duplicado(db, dados):
    u = Usuario(nome="Outra", email="ana@teste.com", senha_hash="x")
    db.session.add(u)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


@pytest.mark.parametrize("preco, duracao", [(Decimal("0"), 30), (Decimal("10"), 0), (Decimal("10"), 500)])
def test_banco_rejeita_preco_ou_duracao_invalidos(db, preco, duracao):
    db.session.add(Servico(nome="Inválido", preco=preco, duracao_min=duracao))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_banco_rejeita_dois_agendamentos_ativos_no_mesmo_inicio(db, dados):
    inicio = datetime(2026, 10, 20, 10, 0)
    for _ in range(2):
        db.session.add(Agendamento(cliente=dados["cliente"], profissional=dados["profissional"],
                                   servico=dados["corte"], inicio=inicio, fim=inicio + timedelta(minutes=30)))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()
