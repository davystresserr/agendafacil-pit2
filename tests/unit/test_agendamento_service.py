from datetime import date, datetime, timedelta

import pytest

from agendafacil.models import StatusAgendamento
from agendafacil.services import agendamento_service as svc
from agendafacil.services.erros import AcessoNegadoError, RegraNegocioError
from tests.conftest import AGORA, criar_usuario

TERCA = date(2026, 10, 20)


def em(h, m=0, dia=TERCA):
    return datetime.combine(dia, datetime.min.time()).replace(hour=h, minute=m)


def test_horarios_livres_respeitam_jornada_e_duracao(dados):
    livres = svc.horarios_livres(dados["profissional"], dados["corte"], TERCA, AGORA)
    assert livres[0] == em(9) and em(11, 30) in livres and em(12) not in livres
    assert em(13) in livres and em(17, 30) in livres and em(18) not in livres
    # serviço de 60 min não cabe às 11:30
    livres_barba = svc.horarios_livres(dados["profissional"], dados["barba"], TERCA, AGORA)
    assert em(11) in livres_barba and em(11, 30) not in livres_barba


def test_horarios_livres_excluem_passado_domingo_e_servico_nao_realizado(dados):
    hoje = AGORA.date()
    agora = AGORA.replace(hour=10, minute=10)
    livres = svc.horarios_livres(dados["profissional"], dados["corte"], hoje, agora)
    assert all(h > agora for h in livres) and livres[0] == em(10, 30, hoje)
    assert svc.horarios_livres(dados["profissional"], dados["corte"], date(2026, 10, 25), AGORA) == []  # domingo
    assert svc.horarios_livres(dados["profissional"], dados["escova"], TERCA, AGORA) == []


def test_agendar_ocupa_horario(dados):
    ag = svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(10), AGORA, "  obs  ")
    assert ag.id and ag.fim == em(10, 30) and ag.status == StatusAgendamento.AGENDADO and ag.observacao == "obs"
    livres = svc.horarios_livres(dados["profissional"], dados["corte"], TERCA, AGORA)
    assert em(10) not in livres and em(9, 30) in livres and em(10, 30) in livres


@pytest.mark.parametrize("inicio", [em(10), em(9, 45), em(10, 15)])
def test_nao_permite_sobreposicao(dados, inicio):
    svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(10), AGORA)
    outro = criar_usuario("Bruno", "bruno@teste.com")
    with pytest.raises(RegraNegocioError, match="ocupado"):
        svc.agendar(outro, dados["profissional"], dados["corte"], inicio, AGORA)


def test_permite_horario_encostado(dados):
    svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(10), AGORA)
    assert svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(10, 30), AGORA).id


@pytest.mark.parametrize("inicio, msg", [
    (AGORA - timedelta(hours=1), "já passou"),
    (em(7), "não atende"),
    (em(11, 45), "não atende"),          # terminaria 12:15, fora da faixa
    (em(10, dia=date(2026, 10, 25)), "não atende"),  # domingo
])
def test_regras_de_horario(dados, inicio, msg):
    with pytest.raises(RegraNegocioError, match=msg):
        svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], inicio, AGORA)


def test_profissional_precisa_realizar_servico_e_servico_ativo(dados, db):
    with pytest.raises(RegraNegocioError, match="não realiza"):
        svc.agendar(dados["cliente"], dados["profissional"], dados["escova"], em(10), AGORA)
    dados["corte"].ativo = False
    with pytest.raises(RegraNegocioError, match="não está disponível"):
        svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(10), AGORA)


def test_somente_cliente_agenda(dados):
    with pytest.raises(AcessoNegadoError):
        svc.agendar(dados["admin"], dados["profissional"], dados["corte"], em(10), AGORA)


def test_cliente_cancela_com_antecedencia_e_libera_horario(dados):
    ag = svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(10), AGORA)
    svc.cancelar(ag, dados["cliente"], AGORA)
    assert ag.status == StatusAgendamento.CANCELADO and ag.cancelado_em == AGORA
    assert em(10) in svc.horarios_livres(dados["profissional"], dados["corte"], TERCA, AGORA)
    with pytest.raises(RegraNegocioError, match="não pode mais"):
        svc.cancelar(ag, dados["cliente"], AGORA)


def test_cliente_nao_cancela_com_menos_de_2_horas(dados):
    ag = svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(10), AGORA)
    with pytest.raises(RegraNegocioError, match="2 horas"):
        svc.cancelar(ag, dados["cliente"], em(8, 1))
    # o profissional pode cancelar mesmo em cima da hora
    svc.cancelar(ag, dados["u_prof"], em(9, 30))
    assert ag.status == StatusAgendamento.CANCELADO


def test_outro_cliente_nao_cancela(dados):
    ag = svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(10), AGORA)
    intruso = criar_usuario("Intruso", "intruso@teste.com")
    with pytest.raises(AcessoNegadoError):
        svc.cancelar(ag, intruso, AGORA)


def test_concluir_atendimento(dados):
    ag = svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(10), AGORA)
    with pytest.raises(RegraNegocioError, match="ainda não começou"):
        svc.concluir(ag, dados["u_prof"], AGORA)
    with pytest.raises(AcessoNegadoError):
        svc.concluir(ag, dados["cliente"], em(10, 5))
    svc.concluir(ag, dados["u_prof"], em(10, 5))
    assert ag.status == StatusAgendamento.CONCLUIDO
    with pytest.raises(RegraNegocioError, match="ativos"):
        svc.concluir(ag, dados["admin"], em(10, 5))


def test_listagens(dados):
    a1 = svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(10), AGORA)
    a2 = svc.agendar(dados["cliente"], dados["profissional"], dados["corte"], em(14), AGORA)
    assert svc.do_cliente(dados["cliente"]) == [a2, a1]
    assert svc.do_profissional(dados["profissional"], a_partir_de=em(12)) == [a2]
    assert len(svc.todos()) == 2
    assert svc.contar_do_dia(TERCA) == 2
