from datetime import datetime

from sqlalchemy import Column, String, DateTime

from db import Base


class UserDAO(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="participant")
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, id, username, email, password_hash, role, full_name=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
