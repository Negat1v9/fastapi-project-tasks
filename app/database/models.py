import sqlalchemy as sa
from . database import Base

"""Main table for contain user with his params"""
class User(Base):
    __tablename__ = "users"
    id = sa.Column(sa.Integer(), primary_key=True, nullable=False)
    first_name = sa.Column(sa.String(255), nullable=False)
    last_name = sa.Column(sa.String(255), nullable=False)
    email = sa.Column(sa.String(), nullable=False, unique=True)
    password = sa.Column(sa.String(255), nullable=False)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True),
                            server_default=sa.text("now()"),
                            nullable=False)
    is_confirmed = sa.Column(sa.Boolean(), server_default="false")
    is_active = sa.Column(sa.Boolean(), server_default="true")
"""Table for contain ordinary users tasks """
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
"""Table for generate group with owner - manager"""
class ManagerGroup(Base):
    __tablename__ = "managersgroups"
    id = sa.Column(sa.Integer(), primary_key=True, nullable=False,
                         autoincrement="auto")
    name = sa.Column(sa.String(255), server_default=sa.text("NULL"))
    manager_id = sa.Column(sa.Integer(), sa.ForeignKey("users.id"),
                        nullable=False)
    is_open = sa.Column(sa.BOOLEAN(), nullable=False,
                        server_default=(sa.text("false")))
""" User can write new task and appoint another user to perform"""
class GeneralMiss(Base):
    __tablename__ = "generalmissions"
    id = sa.Column(sa.Integer(), primary_key=True, nullable=False)
    task = sa.Column(sa.String(), nullable=False)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True),
                           server_default=sa.text("now()"))
    group_id = sa.Column(sa.Integer(),sa.ForeignKey("managersgroups.id",
                                    ondelete=("CASCADE")), nullable=False)
    owner_id = sa.Column(sa.Integer(), sa.ForeignKey(
        "users.id"), nullable=False)    
    debtor_id = sa.Column(sa.Integer(), sa.ForeignKey("users.id"))
"""Table for communication between the group and the user"""
class UserGroup(Base):
    __tablename__ = "usersgroups"
    user_id = sa.Column(sa.Integer(), sa.ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    group_id = sa.Column(sa.Integer(), sa.ForeignKey(
        "managersgroups.id", ondelete="CASCADE"), primary_key=True)
    
class RefreshToken(Base):
    __tablename__ = "refresh_token"
    id = sa.Column(sa.UUID, primary_key=True)
    user_id = sa.Column(sa.ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, primary_key=True)
    refresh_token = sa.Column(sa.String, nullable=False)
    expires_at = sa.Column(sa.DateTime, nullable=False)
    created_at = sa.Column(sa.DateTime, server_default=sa.text("now()"),
                           nullable=False)
    