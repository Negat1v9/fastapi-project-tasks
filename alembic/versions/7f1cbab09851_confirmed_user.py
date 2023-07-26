"""confirmed user

Revision ID: 7f1cbab09851
Revises: 8684303c410f
Create Date: 2023-07-24 18:58:24.263422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f1cbab09851'
down_revision = '8684303c410f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column(
        "is_confirmed", sa.Boolean(),
        server_default=sa.text("false"),
        nullable=False))


def downgrade() -> None:
    op.drop_column("users", "is_confirmed")
