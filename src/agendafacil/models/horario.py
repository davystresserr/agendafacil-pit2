from datetime import datetime

from ..extensions import db

DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


class HorarioDisponivel(db.Model):
    __tablename__ = "horarios_disponiveis"
    __table_args__ = (
        db.CheckConstraint("dia_semana BETWEEN 0 AND 6", name="ck_horarios_dia"),
        db.CheckConstraint("hora_fim > hora_inicio", name="ck_horarios_ordem"),
        db.UniqueConstraint("profissional_id", "dia_semana", "hora_inicio", name="uq_horarios_inicio"),
    )

    id = db.Column(db.Integer, primary_key=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissionais.id", ondelete="CASCADE"), nullable=False)
    dia_semana = db.Column(db.SmallInteger, nullable=False)  # 0 = segunda ... 6 = domingo
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)

    profissional = db.relationship("Profissional", back_populates="horarios")

    @property
    def dia_nome(self) -> str:
        return DIAS_SEMANA[self.dia_semana]

    def contem(self, inicio: datetime, fim: datetime) -> bool:
        """True se o intervalo [inicio, fim) cabe inteiro nesta faixa, no mesmo dia."""
        return (
            inicio.weekday() == self.dia_semana
            and fim.date() == inicio.date()
            and self.hora_inicio <= inicio.time()
            and fim.time() <= self.hora_fim
        )

    def __repr__(self):
        return f"<Horario {self.dia_nome} {self.hora_inicio}-{self.hora_fim}>"
