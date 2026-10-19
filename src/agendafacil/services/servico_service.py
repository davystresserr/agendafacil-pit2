from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Servico
from .erros import ValidacaoError
from .validacao import limpar, validar_duracao, validar_nome, validar_preco

MSG_NOME_DUPLICADO = "Já existe um serviço com este nome."


def listar_ativos():
    return Servico.query.filter_by(ativo=True).order_by(Servico.nome).all()


def listar_todos():
    return Servico.query.order_by(Servico.ativo.desc(), Servico.nome).all()


def _validar(nome, preco, duracao_min, servico_id=None):
    erros = {}
    nome = validar_nome(nome, erros, maximo=80)
    preco = validar_preco(preco, erros)
    duracao = validar_duracao(duracao_min, erros)
    if "nome" not in erros:
        existente = Servico.query.filter(db.func.lower(Servico.nome) == nome.lower()).first()
        if existente and existente.id != servico_id:
            erros["nome"] = MSG_NOME_DUPLICADO
    if erros:
        raise ValidacaoError(erros)
    return nome, preco, duracao


def _salvar():
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValidacaoError({"nome": MSG_NOME_DUPLICADO})


def criar(nome, preco, duracao_min, descricao=None) -> Servico:
    nome, preco, duracao = _validar(nome, preco, duracao_min)
    servico = Servico(nome=nome, preco=preco, duracao_min=duracao, descricao=limpar(descricao) or None)
    db.session.add(servico)
    _salvar()
    return servico


def atualizar(servico: Servico, nome, preco, duracao_min, descricao=None) -> Servico:
    nome, preco, duracao = _validar(nome, preco, duracao_min, servico_id=servico.id)
    servico.nome, servico.preco, servico.duracao_min = nome, preco, duracao
    servico.descricao = limpar(descricao) or None
    _salvar()
    return servico


def alternar_ativo(servico: Servico) -> Servico:
    servico.ativo = not servico.ativo
    db.session.commit()
    return servico
