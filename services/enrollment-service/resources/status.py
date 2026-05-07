import datetime

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from daos.enrollment_dao import EnrollmentDAO
from db import Session


class Status:
    @staticmethod
    def update(e_id, status):
        session = Session()
        enrollment = session.query(EnrollmentDAO).filter(EnrollmentDAO.id == e_id).first()

        if not enrollment:
            session.close()
            return JSONResponse(
                content=jsonable_encoder({"message": f"There is no enrollment with id {e_id}"}),
                status_code=404
            )

        enrollment.status.status_name = status
        enrollment.status.last_update = datetime.datetime.now()

        session.commit()
        session.close()

        return JSONResponse(
            content=jsonable_encoder({"message": "The enrollment status was updated"}),
            status_code=200
        )