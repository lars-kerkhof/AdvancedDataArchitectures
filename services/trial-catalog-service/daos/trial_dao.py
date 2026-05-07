from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime

from db import Base


class TrialDAO(Base):
    __tablename__ = 'trials'

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")
    inclusion_criteria_text = Column(String, nullable=False)
    exclusion_criteria_text = Column(String, default="")
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    condition = Column(String, nullable=False)
    sponsor = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, id, title, status, inclusion_criteria_text, exclusion_criteria_text,
                 min_age, max_age, condition, sponsor=None):
        self.id = id
        self.title = title
        self.status = status
        self.inclusion_criteria_text = inclusion_criteria_text
        self.exclusion_criteria_text = exclusion_criteria_text
        self.min_age = min_age
        self.max_age = max_age
        self.condition = condition
        self.sponsor = sponsor
