# resources/enrollment.py
from datetime import datetime

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from daos.enrollment_dao import EnrollmentDAO
from daos.status_dao import StatusDAO
from db import Session
from pdmodels.enrollment_req import EnrollmentReq
from pdmodels.status_req import STATUS_READY_FOR_CONSENT


class Enrollment:
    @staticmethod
    def create(e_req: EnrollmentReq):
        session = Session()

        enrollment = EnrollmentDAO(
            candidate_id=e_req.candidate_id,
            trial_id=e_req.trial_id,
            match_score=e_req.match_score,
            # FIX: Flatten the array here into the single string BigQuery expects
            match_reason=", ".join(e_req.match_reasons),
            created_at=datetime.now(),
            # FIX: Use the updated relationship name
            status_rel=StatusDAO(STATUS_READY_FOR_CONSENT, datetime.now())
        )

        session.add(enrollment)
        session.commit()
        session.refresh(enrollment)

        output = {
            "enrollment_id": enrollment.id,
            "candidate_id": enrollment.candidate_id,
            "trial_id": enrollment.trial_id,
            "match_score": enrollment.match_score,
            "match_reason": enrollment.match_reason,
            "created_at": enrollment.created_at.isoformat(),
            "status": enrollment.status_rel.status_name
        }

        session.close()

        return JSONResponse(
            content=jsonable_encoder(output),
            status_code=status.HTTP_201_CREATED
        )

    @staticmethod
    def get(e_id):
        session = Session()
        enrollment = session.query(EnrollmentDAO).filter(EnrollmentDAO.id == e_id).first()

        if enrollment:
            status_obj = enrollment.status_rel
            output = {
                "enrollment_id": enrollment.id,
                "candidate_id": enrollment.candidate_id,
                "trial_id": enrollment.trial_id,
                "match_score": enrollment.match_score,
                "match_reason": enrollment.match_reason,
                "created_at": enrollment.created_at.isoformat(),
                "status": {
                    "status": status_obj.status_name,
                    "last_update": status_obj.last_update.isoformat()
                }
            }

            session.close()
            return JSONResponse(content=jsonable_encoder(output), status_code=status.HTTP_200_OK)

        session.close()
        return JSONResponse(
            content=jsonable_encoder({"message": f"There is no enrollment with id {e_id}"}),
            status_code=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def delete(e_id):
        session = Session()
        enrollment = session.query(EnrollmentDAO).filter(EnrollmentDAO.id == e_id).first()

        if enrollment:
            session.delete(enrollment.status_rel)
            session.delete(enrollment)
            session.commit()
            session.close()

            return JSONResponse(
                content=jsonable_encoder({"message": "The enrollment was removed"}),
                status_code=status.HTTP_200_OK
            )

        session.close()
        return JSONResponse(
            content=jsonable_encoder({"message": f"There is no enrollment with id {e_id}"}),
            status_code=status.HTTP_404_NOT_FOUND
        )
