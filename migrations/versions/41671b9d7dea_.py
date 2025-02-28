"""empty message

Revision ID: 41671b9d7dea
Revises: 
Create Date: 2025-02-27 22:15:45.484224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41671b9d7dea'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data_nascimento', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('endereco', sa.String(length=150), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('endereco')
        batch_op.drop_column('data_nascimento')

    # ### end Alembic commands ###
