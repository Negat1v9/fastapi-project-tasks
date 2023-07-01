"""Add groups table

Revision ID: 1c56338775f0
Revises: d4ad7d185e92
Create Date: 2023-06-23 17:22:06.020508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c56338775f0'
down_revision = 'd4ad7d185e92'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('managersgroups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), server_default=sa.text('NULL'), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('generalmissions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.Column('debtor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['debtor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['managersgroups.id'], ),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('usersgroups',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['managersgroups.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'group_id')
    )
    op.add_column('users', sa.Column('first_name', sa.String(length=255), nullable=False))
    op.add_column('users', sa.Column('last_name', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    op.drop_table('usersgroups')
    op.drop_table('generalmissions')
    op.drop_table('managersgroups')
    # ### end Alembic commands ###
