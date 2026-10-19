from sqlalchemy.exc import IntegrityError

from ..extensions import db
from ..models import Papel, Usuario
from .erros import RegraNegocioError, ValidacaoError
from .validacao import validar_email, validar_nome, validar_senha, validar_telefone

MSG_EMAIL_DUPLICADO = "Este e-mail já está cadastrado. Faça login ou use outro e-mail."


def email_em_uso(email: str) -> bool:
    return db.session.query(Usuario.id).filter_by(email=email.strip().lower()).first() is not None


def criar_usuario(nome, email, senha, telefone=None, papel=Papel.CLIENTE, confirmacao=None, commit=True) -> Usuario:
    erros = {}
    nome = validar_nome(nome, erros)
    email = validar_email(email, erros)
    telefone = validar_telefone(telefone, erros)
    senha = validar_senha(senha, confirmacao, erros)
    if papel not in Papel.TODOS:
        erros["papel"] = "Papel inválido."
    if "email" not in erros and email_em_uso(email):
        erros["email"] = MSG_EMAIL_DUPLICADO
    if erros:
        raise ValidacaoError(erros)

    usuario = Usuario(nome=nome, email=email, telefone=telefone, papel=papel)
    usuario.definir_senha(senha)
    db.session.add(usuario)
    if commit:
        try:
            db.session.commit()
        except IntegrityError:  # corrida: outro cadastro com o mesmo e-mail
            db.session.rollback()
            raise ValidacaoError({"email": MSG_EMAIL_DUPLICADO})
    return usuario


def cadastrar_cliente(nome, email, telefone, senha, confirmacao=None) -> Usuario:
    return criar_usuario(nome, email, senha, telefone=telefone, papel=Papel.CLIENTE, confirmacao=confirmacao)


def autenticar(email, senha) -> Usuario:
    email = (email or "").strip().lower()
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario is None or not usuario.ativo or not usuario.verificar_senha(senha or ""):
        raise RegraNegocioError("E-mail ou senha incorretos.")
    return usuario
