"""create_user_table

Revision ID: fab636b98bc7
Revises:
Create Date: 2017-04-17 14:55:22.352000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fab636b98bc7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('character_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('character_owner_hash', sa.String(length=255), nullable=True),
    sa.Column('character_name', sa.String(length=200), nullable=True),
    sa.Column('access_token', sa.String(length=4096), nullable=True),
    sa.Column('access_token_expires', sa.DateTime(), nullable=True),
    sa.Column('refresh_token', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('character_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###