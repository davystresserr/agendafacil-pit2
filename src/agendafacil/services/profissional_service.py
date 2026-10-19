from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import HorarioDisponivel, Papel, Profissional, Servico
from . import auth_service
from .erros import RegraNegocioError, ValidacaoError
from .validacao import converter_hora, converter_int, limpar


def listar_ativos():
    return Profissional.query.filter_by(ativo=True).all()


def listar_todos():
    return Profissional.query.all()


def que_realizam(servico: Servico):
    return [p for p in servico.profissionais if p.ativo and p.usuario.ativo]


def cadastrar(nome, email, senha, especialidade=None, bio=None, servico_ids=()) -> Profissional:
    ids = {i for i in (converter_int(x) for x in servico_ids) if i}
    servicos = Servico.query.filter(Servico.id.in_(ids)).all() if ids else []
    try:
        usuario = auth_service.criar_usuario(nome, email, senha, papel=Papel.PROFISSIONAL, commit=False)
    except ValidacaoError as e:
        if not servicos:
            e.erros["servicos"] = "Selecione pelo menos um serviço."
        raise
    if not servicos:
        db.session.rollback()
        raise ValidacaoError({"servicos": "Selecione pelo menos um serviço."})
    profissional = Profissional(usuario=usuario, especialidade=limpar(especialidade)[:80] or None,
                                bio=limpar(bio) or None, servicos=servicos)
    db.session.add(profissional)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValidacaoError({"email": auth_service.MSG_EMAIL_DUPLICADO})
    return profissional


def adicionar_horario(profissional: Profissional, dia_semana, hora_inicio, hora_fim) -> HorarioDisponivel:
    erros = {}
    dia = converter_int(dia_semana)
    inicio, fim = converter_hora(hora_inicio), converter_hora(hora_fim)
    if dia is None or not 0 <= dia <= 6:
        erros["dia_semana"] = "Escolha um dia da semana."
    if inicio is None:
        erros["hora_inicio"] = "Informe a hora de início."
    if fim is None:
        erros["hora_fim"] = "Informe a hora de fim."
    if inicio and fim and fim <= inicio:
        erros["hora_fim"] = "A hora de fim deve ser depois da hora de início."
    if erros:
        raise ValidacaoError(erros)
    for h in profissional.horarios:
        if h.dia_semana == dia and inicio < h.hora_fim and fim > h.hora_inicio:
            raise RegraNegocioError(
                f"Esse horário se sobrepõe a {h.dia_nome} {h.hora_inicio:%H:%M}–{h.hora_fim:%H:%M} já cadastrado.")
    horario = HorarioDisponivel(profissional=profissional, dia_semana=dia, hora_inicio=inicio, hora_fim=fim)
    db.session.add(horario)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise RegraNegocioError("Já existe um horário com esse início nesse dia.")
    return horario


def remover_horario(profissional: Profissional, horario_id) -> None:
    horario = db.session.get(HorarioDisponivel, converter_int(horario_id) or 0)
    if horario is None or horario.profissional_id != profissional.id:
        raise RegraNegocioError("Horário não encontrado.")
    db.session.delete(horario)
    db.session.commit()
