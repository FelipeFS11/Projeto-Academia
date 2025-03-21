"""Recriando banco

Revision ID: d4be92a4b18e
Revises: 
Create Date: 2025-03-05 22:14:24.598772

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4be92a4b18e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=150), nullable=True),
    sa.Column('last_name', sa.String(length=150), nullable=True),
    sa.Column('email', sa.String(length=150), nullable=False),
    sa.Column('data_nascimento', sa.Date(), nullable=True),
    sa.Column('endereco', sa.String(length=150), nullable=True),
    sa.Column('contato', sa.String(length=50), nullable=True),
    sa.Column('password', sa.String(length=150), nullable=False),
    sa.Column('forma_pagamento', sa.String(length=50), nullable=True),
    sa.Column('ultimo_pagamento', sa.Date(), nullable=True),
    sa.Column('dias_treino', sa.String(length=100), nullable=True),
    sa.Column('peso', sa.Float(), nullable=True),
    sa.Column('altura', sa.Float(), nullable=True),
    sa.Column('imc', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
