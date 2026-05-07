"""Partial update for the 'submit missing intake details' operation.
All fields optional — submitter only sends what they're filling in."""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel

from pdmodels.candidate_req import SexEnum


class IntakeDetailsReq(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[SexEnum] = None
    country: Optional[str] = None
    conditions: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    contact_email_opt_in: Optional[bool] = None
    contact_phone_opt_in: Optional[bool] = None
    preferred_language: Optional[str] = None
