from ..extensions import db
from .profissional import profissional_servico


class Servico(db.Model):
    __tablename__ = "servicos"
    __table_args__ = (
        db.CheckConstraint("preco > 0", name="ck_servicos_preco"),
        db.CheckConstraint("duracao_min BETWEEN 5 AND 480", name="ck_servicos_duracao"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Numeric(8, 2), nullable=False)
    duracao_min = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())

    profissionais = db.relationship("Profissional", secondary=profissional_servico, back_populates="servicos")

    @property
    def preco_formatado(self) -> str:
        valor = f"{self.preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {valor}"

    def __repr__(self):
        return f"<Servico {self.nome}>"
