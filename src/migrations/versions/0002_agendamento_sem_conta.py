"""Agendamento sem conta: nome, telefone e token de acesso no próprio agendamento

Revision ID: 0002_agendamento_sem_conta
Revises: 0001_esquema_inicial
Create Date: 2026-11-10
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_agendamento_sem_conta"
down_revision = "0001_esquema_inicial"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("agendamentos") as t:
        t.alter_column("cliente_id", existing_type=sa.Integer, nullable=True)
        t.add_column(sa.Column("cliente_nome", sa.String(100)))
        t.add_column(sa.Column("cliente_telefone", sa.String(20)))
        t.add_column(sa.Column("token", sa.String(64)))
        t.create_unique_constraint("uq_ag_token", ["token"])
        t.create_check_constraint(
            "ck_ag_cliente",
            "cliente_id IS NOT NULL OR (cliente_nome IS NOT NULL AND cliente_telefone IS NOT NULL AND token IS NOT NULL)")


def downgrade():
    with op.batch_alter_table("agendamentos") as t:
        t.drop_constraint("ck_ag_cliente", type_="check")
        t.drop_constraint("uq_ag_token", type_="unique")
        t.drop_column("token")
        t.drop_column("cliente_telefone")
        t.drop_column("cliente_nome")
        t.alter_column("cliente_id", existing_type=sa.Integer, nullable=False)
