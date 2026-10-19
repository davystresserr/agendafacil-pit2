"""Validações de entrada reutilizadas pelos services (validação no servidor)."""
import re
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TELEFONE_RE = re.compile(r"^[0-9 +()\-]{8,20}$")
SENHA_MIN = 8


def limpar(valor) -> str:
    return (valor or "").strip()


def validar_nome(nome: str, erros: dict, campo="nome", minimo=2, maximo=100) -> str:
    nome = limpar(nome)
    if not nome:
        erros[campo] = f"Preencha o campo {campo}."
    elif len(nome) < minimo or len(nome) > maximo:
        erros[campo] = f"O campo {campo} deve ter entre {minimo} e {maximo} caracteres."
    return nome


def validar_email(email: str, erros: dict) -> str:
    email = limpar(email).lower()
    if not email:
        erros["email"] = "Preencha o campo e-mail."
    elif len(email) > 120 or not EMAIL_RE.match(email):
        erros["email"] = "Informe um e-mail válido."
    return email


def validar_telefone(telefone: str, erros: dict) -> str | None:
    telefone = limpar(telefone)
    if telefone and not TELEFONE_RE.match(telefone):
        erros["telefone"] = "Telefone inválido. Use apenas números, espaços, +, ( ) e -."
    return telefone or None


def validar_senha(senha: str, confirmacao: str | None, erros: dict) -> str:
    senha = senha or ""
    if len(senha) < SENHA_MIN:
        erros["senha"] = f"A senha deve ter pelo menos {SENHA_MIN} caracteres."
    elif confirmacao is not None and senha != confirmacao:
        erros["confirmacao"] = "As senhas não conferem."
    return senha


def validar_preco(valor, erros: dict) -> Decimal | None:
    texto = limpar(str(valor) if valor is not None else "").replace("R$", "").strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        preco = Decimal(texto).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        erros["preco"] = "Informe um preço válido (ex.: 45,00)."
        return None
    if preco <= 0:
        erros["preco"] = "O preço deve ser maior que zero."
    elif preco > Decimal("999999.99"):
        erros["preco"] = "O preço é alto demais."
    return preco


def validar_duracao(valor, erros: dict) -> int | None:
    try:
        duracao = int(str(valor).strip())
    except (TypeError, ValueError):
        erros["duracao_min"] = "Informe a duração em minutos."
        return None
    if not 5 <= duracao <= 480:
        erros["duracao_min"] = "A duração deve estar entre 5 e 480 minutos."
    return duracao


def converter_data(valor) -> date | None:
    try:
        return date.fromisoformat(limpar(valor))
    except (TypeError, ValueError):
        return None


def converter_hora(valor) -> time | None:
    try:
        return time.fromisoformat(limpar(valor))
    except (TypeError, ValueError):
        return None


def converter_datahora(valor) -> datetime | None:
    try:
        return datetime.fromisoformat(limpar(valor)).replace(second=0, microsecond=0, tzinfo=None)
    except (TypeError, ValueError):
        return None


def converter_int(valor) -> int | None:
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return None
