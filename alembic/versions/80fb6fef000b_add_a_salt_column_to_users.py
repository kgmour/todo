"""Add a salt column to users

Revision ID: 80fb6fef000b
Revises: f04f974f6bec
Create Date: 2018-03-12 15:01:02.671673

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80fb6fef000b'
down_revision = 'f04f974f6bec'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('salt', sa.String))


def downgrade():
    op.drop_column('users', 'salt')
