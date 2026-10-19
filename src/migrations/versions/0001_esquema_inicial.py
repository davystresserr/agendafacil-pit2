"""Esquema inicial do AgendaFácil (reproduz docs/situacao-1/modelo-dados/03-projeto-fisico.sql)

Revision ID: 0001_esquema_inicial
Revises:
Create Date: 2026-10-19
"""
import sqlalchemy as sa
from alembic import op

revision = "0001_esquema_inicial"
down_revision = None
branch_labels = None
depends_on = None


def _postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade():
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("email", sa.String(120), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("telefone", sa.String(20)),
        sa.Column("papel", sa.String(15), nullable=False, server_default="cliente"),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("criado_em", sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
        sa.CheckConstraint("papel IN ('cliente', 'profissional', 'admin')", name="ck_usuarios_papel"),
        sa.CheckConstraint("length(trim(nome)) >= 2", name="ck_usuarios_nome"),
        sa.CheckConstraint("email = lower(email) AND email LIKE '%_@_%._%'", name="ck_usuarios_email"),
    )

    op.create_table(
        "profissionais",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("usuario_id", sa.Integer, nullable=False),
        sa.Column("especialidade", sa.String(80)),
        sa.Column("bio", sa.Text),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("usuario_id", name="uq_profissionais_usuario"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], name="fk_profissionais_usuario",
                                ondelete="CASCADE"),
    )

    op.create_table(
        "servicos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("nome", sa.String(80), nullable=False),
        sa.Column("descricao", sa.Text),
        sa.Column("preco", sa.Numeric(8, 2), nullable=False),
        sa.Column("duracao_min", sa.Integer, nullable=False),
        sa.Column("ativo", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("nome", name="uq_servicos_nome"),
        sa.CheckConstraint("preco > 0", name="ck_servicos_preco"),
        sa.CheckConstraint("duracao_min BETWEEN 5 AND 480", name="ck_servicos_duracao"),
    )

    op.create_table(
        "profissional_servico",
        sa.Column("profissional_id", sa.Integer, nullable=False),
        sa.Column("servico_id", sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint("profissional_id", "servico_id", name="pk_profissional_servico"),
        sa.ForeignKeyConstraint(["profissional_id"], ["profissionais.id"], name="fk_ps_profissional",
                                ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["servico_id"], ["servicos.id"], name="fk_ps_servico", ondelete="CASCADE"),
    )
    op.create_index("ix_ps_servico", "profissional_servico", ["servico_id"])

    op.create_table(
        "horarios_disponiveis",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("profissional_id", sa.Integer, nullable=False),
        sa.Column("dia_semana", sa.SmallInteger, nullable=False),
        sa.Column("hora_inicio", sa.Time, nullable=False),
        sa.Column("hora_fim", sa.Time, nullable=False),
        sa.ForeignKeyConstraint(["profissional_id"], ["profissionais.id"], name="fk_horarios_profissional",
                                ondelete="CASCADE"),
        sa.CheckConstraint("dia_semana BETWEEN 0 AND 6", name="ck_horarios_dia"),
        sa.CheckConstraint("hora_fim > hora_inicio", name="ck_horarios_ordem"),
        sa.UniqueConstraint("profissional_id", "dia_semana", "hora_inicio", name="uq_horarios_inicio"),
    )

    op.create_table(
        "agendamentos",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("cliente_id", sa.Integer, nullable=False),
        sa.Column("profissional_id", sa.Integer, nullable=False),
        sa.Column("servico_id", sa.Integer, nullable=False),
        sa.Column("inicio", sa.DateTime, nullable=False),
        sa.Column("fim", sa.DateTime, nullable=False),
        sa.Column("status", sa.String(15), nullable=False, server_default="agendado"),
        sa.Column("observacao", sa.String(255)),
        sa.Column("criado_em", sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("cancelado_em", sa.DateTime),
        sa.ForeignKeyConstraint(["cliente_id"], ["usuarios.id"], name="fk_ag_cliente", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["profissional_id"], ["profissionais.id"], name="fk_ag_profissional",
                                ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["servico_id"], ["servicos.id"], name="fk_ag_servico", ondelete="RESTRICT"),
        sa.CheckConstraint("status IN ('agendado', 'cancelado', 'concluido')", name="ck_ag_status"),
        sa.CheckConstraint("fim > inicio", name="ck_ag_periodo"),
        sa.CheckConstraint("(status = 'cancelado') = (cancelado_em IS NOT NULL)", name="ck_ag_cancelado"),
    )
    op.create_index("ix_ag_profissional_inicio", "agendamentos", ["profissional_id", "inicio"])
    op.create_index("ix_ag_cliente_inicio", "agendamentos", ["cliente_id", "inicio"])
    op.create_index("ix_ag_servico", "agendamentos", ["servico_id"])
    op.create_index("uq_ag_profissional_inicio_ativo", "agendamentos", ["profissional_id", "inicio"], unique=True,
                    sqlite_where=sa.text("status = 'agendado'"), postgresql_where=sa.text("status = 'agendado'"))

    if _postgres():
        op.execute(
            "ALTER TABLE agendamentos ADD CONSTRAINT ex_ag_sem_sobreposicao "
            "EXCLUDE USING gist (int4range(profissional_id, profissional_id, '[]') WITH =, tsrange(inicio, fim, '[)') WITH &&) "
            "WHERE (status = 'agendado')"
        )


def downgrade():
    op.drop_table("agendamentos")
    op.drop_table("horarios_disponiveis")
    op.drop_table("profissional_servico")
    op.drop_table("servicos")
    op.drop_table("profissionais")
    op.drop_table("usuarios")
