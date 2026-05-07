import datetime
import uuid

import bcrypt
from sqlalchemy import Column, String, Boolean, DateTime

from db import Base


class UserDAO(Base):
    """User model for storing user-related details."""
    __tablename__ = "users"

    # String UUID instead of auto-increment integer (BigQuery doesn't auto-increment)
    id = Column(String, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    registered_on = Column(DateTime, nullable=False)
    admin = Column(Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.id = f"user_{uuid.uuid4().hex[:12]}"
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.registered_on = datetime.datetime.now()
        self.admin = admin
