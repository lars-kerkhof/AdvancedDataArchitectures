from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Date

from db import Base


class CandidateDAO(Base):
    __tablename__ = 'candidates'

    id = Column(String, primary_key=True)

    # Demographics
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=False)
    sex = Column(String, nullable=False)
    country = Column(String, nullable=False)

    # Medical (stored as JSON strings — encoded in resource layer)
    conditions = Column(String, default="[]")
    medications = Column(String, default="[]")
    allergies = Column(String, default="[]")

    # Contact preferences
    contact_email_opt_in = Column(Boolean, default=True)
    contact_phone_opt_in = Column(Boolean, default=False)
    preferred_language = Column(String, default="en")

    # State
    outreach_state = Column(String, default="not_contacted")
    recruitment_status = Column(String, default="submitted")
    enrolled = Column(Boolean, nullable=False, default=False)

    # Audit
    intake_submitted_at = Column(DateTime, default=datetime.utcnow)
    last_intake_update_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, id, full_name, email, date_of_birth, sex, country,
                 phone=None,
                 conditions="[]", medications="[]", allergies="[]",
                 contact_email_opt_in=True, contact_phone_opt_in=False,
                 preferred_language="en"):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.date_of_birth = date_of_birth
        self.sex = sex
        self.country = country
        self.conditions = conditions
        self.medications = medications
        self.allergies = allergies
        self.contact_email_opt_in = contact_email_opt_in
        self.contact_phone_opt_in = contact_phone_opt_in
        self.preferred_language = preferred_language
