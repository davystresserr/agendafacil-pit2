"""Regras de negócio do agendamento (RN01, RN02, RN03, RN06, RN07)."""
import secrets
from datetime import date, datetime, timedelta

from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Agendamento, Profissional, Servico, StatusAgendamento, Usuario
from .erros import AcessoNegadoError, RegraNegocioError, ValidacaoError
from .validacao import limpar, validar_nome, validar_telefone

PASSO_MIN = 30  # intervalo entre inícios de horários oferecidos ao cliente

MSG_OCUPADO = "Este horário acabou de ser ocupado. Escolha outro horário."
MSG_PASSADO = "Não é possível agendar em um horário que já passou."
MSG_FORA_JORNADA = "O profissional não atende nesse horário."
MSG_CANCELAMENTO_TARDIO = ("Cancelamento só é permitido com pelo menos 2 horas de antecedência. "
                           "Entre em contato com o salão.")


def _ocupados(profissional_id: int, inicio: datetime, fim: datetime, ignorar_id=None):
    q = Agendamento.query.filter(
        Agendamento.profissional_id == profissional_id,
        Agendamento.status == StatusAgendamento.AGENDADO,
        Agendamento.inicio < fim,
        Agendamento.fim > inicio,
    )
    if ignorar_id:
        q = q.filter(Agendamento.id != ignorar_id)
    return q.all()


def horarios_do_dia(profissional: Profissional, servico: Servico, dia: date,
                    agora: datetime) -> list[tuple[datetime, bool]]:
    """Inícios da jornada no dia, cada um com True se está livre (no futuro e sem sobreposição)."""
    if not (profissional.ativo and servico.ativo and profissional.realiza(servico)):
        return []
    duracao = timedelta(minutes=servico.duracao_min)
    passo = timedelta(minutes=PASSO_MIN)
    inicio_dia = datetime.combine(dia, datetime.min.time())
    ocupados = _ocupados(profissional.id, inicio_dia, inicio_dia + timedelta(days=1))

    horarios = {}
    for faixa in profissional.horarios:
        if faixa.dia_semana != dia.weekday():
            continue
        candidato = datetime.combine(dia, faixa.hora_inicio)
        limite = datetime.combine(dia, faixa.hora_fim)
        while candidato + duracao <= limite:
            fim = candidato + duracao
            horarios[candidato] = candidato > agora and not any(
                a.inicio < fim and a.fim > candidato for a in ocupados)
            candidato += passo
    return sorted(horarios.items())


def horarios_livres(profissional: Profissional, servico: Servico, dia: date, agora: datetime) -> list[datetime]:
    """Inícios possíveis no dia: dentro da jornada, no futuro e sem sobreposição."""
    return [h for h, livre in horarios_do_dia(profissional, servico, dia, agora) if livre]


def agendar(cliente: Usuario, profissional: Profissional, servico: Servico, inicio: datetime,
            agora: datetime, observacao: str | None = None) -> Agendamento:
    if not cliente.is_cliente:
        raise AcessoNegadoError("Apenas clientes podem fazer agendamentos.")
    return _criar({"cliente": cliente}, profissional, servico, inicio, agora, observacao)


def agendar_sem_conta(nome: str, telefone: str, profissional: Profissional, servico: Servico, inicio: datetime,
                      agora: datetime, observacao: str | None = None) -> Agendamento:
    """Agendamento sem cadastro: o cliente informa nome e celular e recebe um link privado (token)."""
    erros = {}
    nome = validar_nome(nome, erros)
    telefone = validar_telefone(telefone, erros)
    if not telefone and "telefone" not in erros:
        erros["telefone"] = "Preencha o campo celular."
    if erros:
        raise ValidacaoError(erros)
    dono = {"cliente_nome": nome, "cliente_telefone": telefone, "token": secrets.token_urlsafe(32)}
    return _criar(dono, profissional, servico, inicio, agora, observacao)


def _criar(dono: dict, profissional: Profissional, servico: Servico, inicio: datetime,
           agora: datetime, observacao: str | None) -> Agendamento:
    if not servico.ativo:
        raise RegraNegocioError("Este serviço não está disponível.")
    if not profissional.ativo or not profissional.realiza(servico):
        raise RegraNegocioError("Este profissional não realiza o serviço escolhido.")
    inicio = inicio.replace(second=0, microsecond=0)
    fim = inicio + timedelta(minutes=servico.duracao_min)
    if inicio <= agora:
        raise RegraNegocioError(MSG_PASSADO)
    if not any(f.contem(inicio, fim) for f in profissional.horarios):
        raise RegraNegocioError(MSG_FORA_JORNADA)
    if _ocupados(profissional.id, inicio, fim):
        raise RegraNegocioError(MSG_OCUPADO)

    agendamento = Agendamento(**dono, profissional=profissional, servico=servico,
                              inicio=inicio, fim=fim, observacao=limpar(observacao)[:255] or None)
    db.session.add(agendamento)
    try:
        db.session.commit()
    except IntegrityError:
        # Dois clientes confirmaram ao mesmo tempo: o banco (EXCLUDE / índice único) barrou o segundo.
        db.session.rollback()
        raise RegraNegocioError(MSG_OCUPADO)
    return agendamento


def _pode_gerenciar(agendamento: Agendamento, usuario: Usuario) -> bool:
    if usuario.is_admin:
        return True
    if usuario.is_profissional:
        return usuario.profissional is not None and usuario.profissional.id == agendamento.profissional_id
    return agendamento.cliente_id == usuario.id


def cancelar(agendamento: Agendamento, usuario: Usuario, agora: datetime) -> Agendamento:
    if not _pode_gerenciar(agendamento, usuario):
        raise AcessoNegadoError()
    if not agendamento.ativo:
        raise RegraNegocioError("Este agendamento não pode mais ser cancelado.")
    if usuario.is_cliente and not agendamento.pode_ser_cancelado_por_cliente(agora):
        raise RegraNegocioError(MSG_CANCELAMENTO_TARDIO)
    agendamento.status = StatusAgendamento.CANCELADO
    agendamento.cancelado_em = agora
    db.session.commit()
    return agendamento


def cancelar_pelo_link(agendamento: Agendamento, agora: datetime) -> Agendamento:
    """Cancelamento por quem tem o link do agendamento sem conta (o token já foi conferido)."""
    if not agendamento.ativo:
        raise RegraNegocioError("Este agendamento não pode mais ser cancelado.")
    if not agendamento.pode_ser_cancelado_por_cliente(agora):
        raise RegraNegocioError(MSG_CANCELAMENTO_TARDIO)
    agendamento.status = StatusAgendamento.CANCELADO
    agendamento.cancelado_em = agora
    db.session.commit()
    return agendamento


def pelo_token(token: str) -> Agendamento | None:
    return Agendamento.query.filter_by(token=token).first() if token else None


def pelos_tokens(tokens: list[str]):
    if not tokens:
        return []
    return Agendamento.query.filter(Agendamento.token.in_(tokens)).order_by(Agendamento.inicio.desc()).all()


def concluir(agendamento: Agendamento, usuario: Usuario, agora: datetime) -> Agendamento:
    if usuario.is_cliente or not _pode_gerenciar(agendamento, usuario):
        raise AcessoNegadoError()
    if not agendamento.ativo:
        raise RegraNegocioError("Só é possível concluir agendamentos ativos.")
    if agendamento.inicio > agora:
        raise RegraNegocioError("O atendimento ainda não começou.")
    agendamento.status = StatusAgendamento.CONCLUIDO
    db.session.commit()
    return agendamento


def do_cliente(cliente: Usuario):
    return (Agendamento.query.filter_by(cliente_id=cliente.id)
            .order_by(Agendamento.inicio.desc()).all())


def do_profissional(profissional: Profissional, a_partir_de: datetime | None = None):
    q = Agendamento.query.filter_by(profissional_id=profissional.id)
    if a_partir_de is not None:
        q = q.filter(Agendamento.inicio >= a_partir_de)
    return q.order_by(Agendamento.inicio).all()


def todos(limite: int = 200):
    return Agendamento.query.order_by(Agendamento.inicio.desc()).limit(limite).all()


def contar_do_dia(dia: date) -> int:
    inicio = datetime.combine(dia, datetime.min.time())
    return Agendamento.query.filter(
        Agendamento.status == StatusAgendamento.AGENDADO,
        Agendamento.inicio >= inicio, Agendamento.inicio < inicio + timedelta(days=1),
    ).count()
