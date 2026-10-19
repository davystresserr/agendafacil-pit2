from datetime import datetime, timedelta

from ..extensions import db


class StatusAgendamento:
    AGENDADO = "agendado"
    CANCELADO = "cancelado"
    CONCLUIDO = "concluido"
    TODOS = (AGENDADO, CANCELADO, CONCLUIDO)
    ROTULOS = {AGENDADO: "Agendado", CANCELADO: "Cancelado", CONCLUIDO: "Concluído"}


ANTECEDENCIA_CANCELAMENTO = timedelta(hours=2)


class Agendamento(db.Model):
    __tablename__ = "agendamentos"
    __table_args__ = (
        db.CheckConstraint("status IN ('agendado', 'cancelado', 'concluido')", name="ck_ag_status"),
        db.CheckConstraint("fim > inicio", name="ck_ag_periodo"),
        db.CheckConstraint("(status = 'cancelado') = (cancelado_em IS NOT NULL)", name="ck_ag_cancelado"),
        db.Index("ix_ag_profissional_inicio", "profissional_id", "inicio"),
        db.Index("ix_ag_cliente_inicio", "cliente_id", "inicio"),
        db.Index("ix_ag_servico", "servico_id"),
        db.Index("uq_ag_profissional_inicio_ativo", "profissional_id", "inicio", unique=True,
                 sqlite_where=db.text("status = 'agendado'"), postgresql_where=db.text("status = 'agendado'")),
    )

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissionais.id", ondelete="RESTRICT"), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey("servicos.id", ondelete="RESTRICT"), nullable=False)
    inicio = db.Column(db.DateTime, nullable=False)
    fim = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(15), nullable=False, default=StatusAgendamento.AGENDADO,
                       server_default=StatusAgendamento.AGENDADO)
    observacao = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now, server_default=db.func.current_timestamp())
    cancelado_em = db.Column(db.DateTime)

    cliente = db.relationship("Usuario", back_populates="agendamentos", foreign_keys=[cliente_id])
    profissional = db.relationship("Profissional", back_populates="agendamentos")
    servico = db.relationship("Servico")

    @property
    def ativo(self) -> bool:
        return self.status == StatusAgendamento.AGENDADO

    @property
    def status_rotulo(self) -> str:
        return StatusAgendamento.ROTULOS.get(self.status, self.status)

    def pode_ser_cancelado_por_cliente(self, agora: datetime) -> bool:
        return self.ativo and self.inicio - agora >= ANTECEDENCIA_CANCELAMENTO

    def __repr__(self):
        return f"<Agendamento {self.id} {self.inicio:%d/%m %H:%M} {self.status}>"
