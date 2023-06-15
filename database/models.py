import sqlalchemy as sa
from . database import Base


class User(Base):
    __tablename__ = "users"
    id = sa.Column(sa.Integer(), primary_key=True, nullable=False)
    email = sa.Column(sa.String(), nullable=False, unique=True)
    password = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True),
                            server_default=sa.text("now()"),
                            nullable=False)
    is_active = sa.Column(sa.Boolean(), server_default="true")
    
class Mission(Base):
    __tablename__ = "missions"
    id = sa.Column(sa.Integer(), primary_key=True, nullable=False)
    task = sa.Column(sa.Text(), nullable=False)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True),
                            server_default=sa.text("now()"),
                            nullable=False)
    owner_id = sa.Column(sa.Integer(),
                            sa.ForeignKey("users.id", ondelete="CASCADE"),
                            nullable=False)
    
    