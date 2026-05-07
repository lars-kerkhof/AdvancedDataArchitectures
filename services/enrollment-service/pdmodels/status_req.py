from enum import Enum
from pydantic import BaseModel


STATUS_READY_FOR_CONSENT = "Ready for consent"
STATUS_CONSENT_IN_PROGRESS = "Consent in progress"
STATUS_CONSENT_COMPLETED = "Consent completed"
STATUS_ENROLLED = "Enrolled"
STATUS_REJECTED = "Rejected"
STATUS_MANUAL_REVIEW_REQUIRED = "Manual review required"


class StatusEnum(str, Enum):
    ready_for_consent = STATUS_READY_FOR_CONSENT
    consent_in_progress = STATUS_CONSENT_IN_PROGRESS
    consent_completed = STATUS_CONSENT_COMPLETED
    enrolled = STATUS_ENROLLED
    rejected = STATUS_REJECTED
    manual_review_required = STATUS_MANUAL_REVIEW_REQUIRED


class StatusModel(BaseModel):
    status: StatusEnum = StatusEnum.ready_for_consent