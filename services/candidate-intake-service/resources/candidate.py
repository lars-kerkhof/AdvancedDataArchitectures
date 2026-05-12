import json
import uuid
from datetime import datetime
from typing import Optional

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from daos.candidate_dao import CandidateDAO
from db import Session
from pdmodels.candidate_req import CandidateReq, RecruitmentStatusEnum
from pdmodels.candidate_res import CandidateRes, RecruitmentStatusRes
from pdmodels.intake_details_req import IntakeDetailsReq
from pdmodels.recruitment_status_req import RecruitmentStatusReq


def _to_response(dao: CandidateDAO) -> dict:
    """Convert a CandidateDAO (with JSON-encoded list fields) to a dict
    matching CandidateRes. We hand-build the dict because JSON list
    fields need decoding before Pydantic sees them."""
    return CandidateRes(
        id=dao.id,
        full_name=dao.full_name,
        email=dao.email,
        phone=dao.phone,
        date_of_birth=dao.date_of_birth,
        sex=dao.sex,
        country=dao.country,
        conditions=json.loads(dao.conditions or "[]"),
        medications=json.loads(dao.medications or "[]"),
        allergies=json.loads(dao.allergies or "[]"),
        contact_email_opt_in=dao.contact_email_opt_in,
        contact_phone_opt_in=dao.contact_phone_opt_in,
        preferred_language=dao.preferred_language,
        outreach_state=dao.outreach_state,
        recruitment_status=dao.recruitment_status,
        enrolled=dao.enrolled,
        intake_submitted_at=dao.intake_submitted_at,
        last_intake_update_at=dao.last_intake_update_at,
        created_at=dao.created_at,
        updated_at=dao.updated_at,
    ).model_dump()


class Candidate:
    @staticmethod
    def create(c_req: CandidateReq):
        session = Session()
        try:
            candidate = CandidateDAO(
                id=f"cand_{uuid.uuid4().hex[:12]}",
                full_name=c_req.full_name,
                email=c_req.email,
                phone=c_req.phone,
                date_of_birth=c_req.date_of_birth,
                sex=c_req.sex.value,
                country=c_req.country,
                conditions=json.dumps(c_req.conditions),
                medications=json.dumps(c_req.medications),
                allergies=json.dumps(c_req.allergies),
                contact_email_opt_in=c_req.contact_email_opt_in,
                contact_phone_opt_in=c_req.contact_phone_opt_in,
                preferred_language=c_req.preferred_language,
            )
            session.add(candidate)
            session.commit()
            session.refresh(candidate)
            return JSONResponse(
                content=jsonable_encoder(_to_response(candidate)),
                status_code=status.HTTP_201_CREATED,
            )
        finally:
            session.close()

    @staticmethod
    def get(c_id: str):
        session = Session()
        try:
            candidate = session.query(CandidateDAO).filter(CandidateDAO.id == c_id).first()
            if not candidate:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"No candidate with id {c_id}"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            return JSONResponse(
                content=jsonable_encoder(_to_response(candidate)),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()

    @staticmethod
    def list(recruitment_status: Optional[RecruitmentStatusEnum] = None):
        session = Session()
        try:
            query = session.query(CandidateDAO)
            if recruitment_status:
                query = query.filter(CandidateDAO.recruitment_status == recruitment_status.value)
            candidates = query.limit(1000).all()
            responses = [_to_response(c) for c in candidates]
            return JSONResponse(
                content=jsonable_encoder(responses),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()

    @staticmethod
    def update(c_id: str, c_req: CandidateReq):
        """Full profile update."""
        session = Session()
        try:
            candidate = session.query(CandidateDAO).filter(CandidateDAO.id == c_id).first()
            if not candidate:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"No candidate with id {c_id}"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            candidate.full_name = c_req.full_name
            candidate.email = c_req.email
            candidate.phone = c_req.phone
            candidate.date_of_birth = c_req.date_of_birth
            candidate.sex = c_req.sex.value
            candidate.country = c_req.country
            candidate.conditions = json.dumps(c_req.conditions)
            candidate.medications = json.dumps(c_req.medications)
            candidate.allergies = json.dumps(c_req.allergies)
            candidate.contact_email_opt_in = c_req.contact_email_opt_in
            candidate.contact_phone_opt_in = c_req.contact_phone_opt_in
            candidate.preferred_language = c_req.preferred_language
            session.commit()
            session.refresh(candidate)
            return JSONResponse(
                content=jsonable_encoder(_to_response(candidate)),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()

    @staticmethod
    def submit_intake_details(c_id: str, details: IntakeDetailsReq):
        """Partial update — sets last_intake_update_at. Only provided fields change."""
        session = Session()
        try:
            candidate = session.query(CandidateDAO).filter(CandidateDAO.id == c_id).first()
            if not candidate:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"No candidate with id {c_id}"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            # Apply only the provided fields
            data = details.model_dump(exclude_unset=True)
            for key, value in data.items():
                if key in ("conditions", "medications", "allergies"):
                    setattr(candidate, key, json.dumps(value))
                elif key == "sex" and value is not None:
                    candidate.sex = value.value if hasattr(value, "value") else value
                else:
                    setattr(candidate, key, value)

            candidate.last_intake_update_at = datetime.utcnow()
            session.commit()
            session.refresh(candidate)
            return JSONResponse(
                content=jsonable_encoder(_to_response(candidate)),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()

    @staticmethod
    def get_recruitment_status(c_id: str):
        session = Session()
        try:
            candidate = session.query(CandidateDAO).filter(CandidateDAO.id == c_id).first()
            if not candidate:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"No candidate with id {c_id}"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            response = RecruitmentStatusRes(
                id=candidate.id,
                recruitment_status=candidate.recruitment_status,
                updated_at=candidate.updated_at,
            )
            return JSONResponse(
                content=jsonable_encoder(response.model_dump()),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()

    @staticmethod
    def update_recruitment_status(c_id: str, status_req: RecruitmentStatusReq):
        session = Session()
        try:
            candidate = session.query(CandidateDAO).filter(CandidateDAO.id == c_id).first()
            if not candidate:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"No candidate with id {c_id}"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            candidate.recruitment_status = status_req.recruitment_status.value
            session.commit()
            session.refresh(candidate)
            response = RecruitmentStatusRes(
                id=candidate.id,
                recruitment_status=candidate.recruitment_status,
                updated_at=candidate.updated_at,
            )
            return JSONResponse(
                content=jsonable_encoder(response.model_dump()),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()

    @staticmethod
    def delete(c_id: str):
        session = Session()
        try:
            candidate = session.query(CandidateDAO).filter(CandidateDAO.id == c_id).first()
            if not candidate:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"No candidate with id {c_id}"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            session.delete(candidate)
            session.commit()
            return JSONResponse(
                content=jsonable_encoder({"message": "The candidate was removed"}),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()
