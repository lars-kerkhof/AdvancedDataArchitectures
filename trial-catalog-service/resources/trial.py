import uuid
from typing import Optional

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from daos.trial_dao import TrialDAO
from db import Session
from pdmodels.trial_req import TrialReq, TrialStatusEnum
from pdmodels.trial_res import TrialRes


class Trial:
    @staticmethod
    def create(t_req: TrialReq):
        session = Session()
        try:
            trial = TrialDAO(
                id=f"trial_{uuid.uuid4().hex[:12]}",
                title=t_req.title,
                status=t_req.status.value,
                inclusion_criteria_text=t_req.inclusion_criteria_text,
                exclusion_criteria_text=t_req.exclusion_criteria_text,
                min_age=t_req.min_age,
                max_age=t_req.max_age,
                condition=t_req.condition,
                sponsor=t_req.sponsor,
            )
            session.add(trial)
            session.commit()
            session.refresh(trial)
            response = TrialRes.model_validate(trial)
            return JSONResponse(
                content=jsonable_encoder(response.model_dump()),
                status_code=status.HTTP_201_CREATED,
            )
        finally:
            session.close()

    @staticmethod
    def get(t_id: str):
        session = Session()
        try:
            trial = session.query(TrialDAO).filter(TrialDAO.id == t_id).first()
            if not trial:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"No trial with id {t_id}"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            response = TrialRes.model_validate(trial)
            return JSONResponse(
                content=jsonable_encoder(response.model_dump()),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()

    @staticmethod
    def list(status_filter: Optional[TrialStatusEnum] = None):
        session = Session()
        try:
            query = session.query(TrialDAO)
            if status_filter:
                query = query.filter(TrialDAO.status == status_filter.value)
            trials = query.limit(1000).all()
            responses = [TrialRes.model_validate(t).model_dump() for t in trials]
            return JSONResponse(
                content=jsonable_encoder(responses),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()

    @staticmethod
    def update(t_id: str, t_req: TrialReq):
        session = Session()
        try:
            trial = session.query(TrialDAO).filter(TrialDAO.id == t_id).first()
            if not trial:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"No trial with id {t_id}"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            trial.title = t_req.title
            trial.status = t_req.status.value
            trial.inclusion_criteria_text = t_req.inclusion_criteria_text
            trial.exclusion_criteria_text = t_req.exclusion_criteria_text
            trial.min_age = t_req.min_age
            trial.max_age = t_req.max_age
            trial.condition = t_req.condition
            trial.sponsor = t_req.sponsor
            session.commit()
            session.refresh(trial)
            response = TrialRes.model_validate(trial)
            return JSONResponse(
                content=jsonable_encoder(response.model_dump()),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()

    @staticmethod
    def delete(t_id: str):
        session = Session()
        try:
            trial = session.query(TrialDAO).filter(TrialDAO.id == t_id).first()
            if not trial:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"No trial with id {t_id}"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            session.delete(trial)
            session.commit()
            return JSONResponse(
                content=jsonable_encoder({"message": "The trial was removed"}),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()
