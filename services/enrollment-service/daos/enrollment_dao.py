from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from daos.status_dao import StatusDAO
from db import Base


class EnrollmentDAO(Base):
    __tablename__ = "enrollment"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(String)
    trial_id = Column(String)
    screening_result_id = Column(String)
    created_at = Column(DateTime)

    status_id = Column(Integer, ForeignKey("status.id"))
    status = relationship(
        StatusDAO.__name__,
        backref=backref("enrollment", uselist=False, cascade="all, delete")
    )

    def __init__(self, candidate_id, trial_id, screening_result_id, created_at, status):
        self.id = id
        self.candidate_id = candidate_id
        self.trial_id = trial_id
        self.screening_result_id = screening_result_id
        self.created_at = created_at
        self.status = status
