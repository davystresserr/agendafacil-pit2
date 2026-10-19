from ..extensions import db

profissional_servico = db.Table(
    "profissional_servico",
    db.Column("profissional_id", db.Integer, db.ForeignKey("profissionais.id", ondelete="CASCADE"), primary_key=True),
    db.Column("servico_id", db.Integer, db.ForeignKey("servicos.id", ondelete="CASCADE"), primary_key=True),
    db.Index("ix_ps_servico", "servico_id"),
)


class Profissional(db.Model):
    __tablename__ = "profissionais"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, unique=True)
    especialidade = db.Column(db.String(80))
    bio = db.Column(db.Text)
    ativo = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())

    usuario = db.relationship("Usuario", back_populates="profissional")
    servicos = db.relationship("Servico", secondary=profissional_servico, back_populates="profissionais",
                               order_by="Servico.nome")
    horarios = db.relationship("HorarioDisponivel", back_populates="profissional", cascade="all, delete-orphan",
                               order_by="(HorarioDisponivel.dia_semana, HorarioDisponivel.hora_inicio)")
    agendamentos = db.relationship("Agendamento", back_populates="profissional")

    @property
    def nome(self) -> str:
        return self.usuario.nome if self.usuario else ""

    def realiza(self, servico) -> bool:
        return any(s.id == servico.id for s in self.servicos)

    def __repr__(self):
        return f"<Profissional {self.nome}>"
