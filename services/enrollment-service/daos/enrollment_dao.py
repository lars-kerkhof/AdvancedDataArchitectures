from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from daos.status_dao import StatusDAO
from db import Base


class EnrollmentDAO(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(String, nullable=False)
    trial_id = Column(String, nullable=False)
    match_score = Column(Integer, nullable=False)
    match_reason = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    status_id = Column(Integer, ForeignKey("status.id"))
    status = relationship(
        StatusDAO.__name__,
        backref=backref("enrollment", uselist=False, cascade="all, delete")
    )

    def __init__(self, candidate_id, trial_id, match_score, match_reason, created_at, status):
        self.candidate_id = candidate_id
        self.trial_id = trial_id  
        self.match_score = match_score
        self.match_reason = match_reason
        self.created_at = created_at
        self.status = status
