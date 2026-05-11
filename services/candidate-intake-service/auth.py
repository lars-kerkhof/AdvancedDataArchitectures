"""JWT verification via iam-service /verify."""
import os
from typing import Optional

import requests
from fastapi import Header, HTTPException

IAM_URL = os.environ.get("IAM_URL")
VERIFY_TIMEOUT_SECONDS = 3


def _verify(authorization: Optional[str]) -> dict:
    if not IAM_URL:
        raise HTTPException(status_code=500, detail="IAM_URL not configured")
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        resp = requests.get(
            f"{IAM_URL}/verify",
            headers={"Authorization": authorization},
            timeout=VERIFY_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Auth service unavailable")

    if resp.status_code != 200:
        try:
            message = resp.json().get("message", "Unauthorized")
        except ValueError:
            message = "Unauthorized"
        raise HTTPException(status_code=resp.status_code, detail=message)

    return resp.json()["data"]


def require_user(authorization: Optional[str] = Header(None)) -> dict:
    return _verify(authorization)


def require_admin(authorization: Optional[str] = Header(None)) -> dict:
    user = _verify(authorization)
    if not user.get("admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
