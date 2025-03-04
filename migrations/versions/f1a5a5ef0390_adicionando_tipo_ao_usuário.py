"""Adicionando tipo ao usuário

Revision ID: f1a5a5ef0390
Revises: c67f5de3d942
Create Date: 2025-03-03 22:22:15.685680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a5a5ef0390'
down_revision = 'c67f5de3d942'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tipo', sa.String(length=10), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('tipo')

    # ### end Alembic commands ###
