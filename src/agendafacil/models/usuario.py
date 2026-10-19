from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db


class Papel:
    CLIENTE = "cliente"
    PROFISSIONAL = "profissional"
    ADMIN = "admin"
    TODOS = (CLIENTE, PROFISSIONAL, ADMIN)


class Usuario(db.Model):
    __tablename__ = "usuarios"
    __table_args__ = (
        db.CheckConstraint("papel IN ('cliente', 'profissional', 'admin')", name="ck_usuarios_papel"),
        db.CheckConstraint("length(trim(nome)) >= 2", name="ck_usuarios_nome"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20))
    papel = db.Column(db.String(15), nullable=False, default=Papel.CLIENTE, server_default=Papel.CLIENTE)
    ativo = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=db.func.current_timestamp())

    profissional = db.relationship("Profissional", back_populates="usuario", uselist=False)
    agendamentos = db.relationship("Agendamento", back_populates="cliente", foreign_keys="Agendamento.cliente_id")

    def definir_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_admin(self) -> bool:
        return self.papel == Papel.ADMIN

    @property
    def is_profissional(self) -> bool:
        return self.papel == Papel.PROFISSIONAL

    @property
    def is_cliente(self) -> bool:
        return self.papel == Papel.CLIENTE

    @property
    def primeiro_nome(self) -> str:
        return self.nome.split()[0] if self.nome else ""

    def __repr__(self):
        return f"<Usuario {self.email} ({self.papel})>"
