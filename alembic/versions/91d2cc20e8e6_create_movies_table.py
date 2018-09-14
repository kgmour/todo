"""create movies table

Revision ID: 91d2cc20e8e6
Revises: 
Create Date: 2018-03-05 10:41:58.197653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91d2cc20e8e6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'movie',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Unicode(500)),
    )


def downgrade():
    op.drop_table('movie')
