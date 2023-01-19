"""empty message

Revision ID: d40bf9b68384
Revises: 68dfdedeb4c4
Create Date: 2023-01-19 15:01:25.876084

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd40bf9b68384'
down_revision = '68dfdedeb4c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('point', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'point')
    # ### end Alembic commands ###