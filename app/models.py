from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    admin_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)


class Member(Base):
    __tablename__ = "members"

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User")


class Vote(Base):
    __tablename__ = "votes"

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class Comment(Base):
    __tablename__ = "comments"

    content = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

