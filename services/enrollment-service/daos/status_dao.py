# daos/status_dao.py

import uuid

from sqlalchemy import Column, String, TIMESTAMP

from db import Base


class StatusDAO(Base):
    __tablename__ = "status"

    id = Column(String, primary_key=True)
    status_name = Column(String)
    last_update = Column(TIMESTAMP(timezone=False))

    def __init__(self, status, last_update):
        self.id = f"status_{uuid.uuid4().hex[:12]}"
        self.status_name = status
        self.last_update = last_update
