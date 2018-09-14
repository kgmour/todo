"""add column to users table

Revision ID: f04f974f6bec
Revises: 91d2cc20e8e6
Create Date: 2018-03-07 16:01:04.724805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f04f974f6bec'
down_revision = '91d2cc20e8e6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('password', sa.String))


def downgrade():
    op.drop_column('users', 'password')
