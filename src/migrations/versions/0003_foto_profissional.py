"""Foto do profissional (endereço da imagem) e fotos dos profissionais de demonstração

Revision ID: 0003_foto_profissional
Revises: 0002_agendamento_sem_conta
Create Date: 2026-11-10
"""
import sqlalchemy as sa
from alembic import op

revision = "0003_foto_profissional"
down_revision = "0002_agendamento_sem_conta"
branch_labels = None
depends_on = None

DEMO = {
    "carlos@agendafacil.com": "https://images.unsplash.com/photo-1598524374912-6b0b0bab43dd?w=400&h=400&fit=crop&crop=faces&q=70",
    "ana@agendafacil.com": "https://images.unsplash.com/photo-1617690825153-8bb0a8e3c911?w=400&h=400&fit=crop&crop=faces&q=70",
}


def upgrade():
    op.add_column("profissionais", sa.Column("foto_url", sa.String(500)))
    for email, url in DEMO.items():
        op.execute(sa.text("UPDATE profissionais SET foto_url = :url WHERE foto_url IS NULL AND usuario_id = "
                           "(SELECT id FROM usuarios WHERE email = :email)").bindparams(url=url, email=email))


def downgrade():
    op.drop_column("profissionais", "foto_url")
