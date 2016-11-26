"""Add tables to store users and their saved search terms.

Revision ID: d3ce41a7b4d3
Revises: 2334ba39b028
Create Date: 2016-11-20 09:50:27.261748

"""

# revision identifiers, used by Alembic.
revision = 'd3ce41a7b4d3'
down_revision = '2334ba39b028'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('social_id', sa.String(length=64), nullable=False),
    sa.Column('nickname', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('social_id')
    )
    op.create_table('searches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('search_terms', sa.String(length=64), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('searches')
    op.drop_table('users')
    ### end Alembic commands ###