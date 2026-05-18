"""Cached service-account JWT for outbound calls to protected services."""
import os
import threading
import time
from typing import Optional

import requests

IAM_URL = os.environ.get("IAM_URL")
SERVICE_ACCOUNT_EMAIL = os.environ.get("SERVICE_ACCOUNT_EMAIL")
SERVICE_ACCOUNT_PASSWORD = os.environ.get("SERVICE_ACCOUNT_PASSWORD")

TOKEN_LIFETIME_SECONDS = 3600
REFRESH_BUFFER_SECONDS = 300
LOGIN_TIMEOUT_SECONDS = 5

_lock = threading.Lock()
_cached_token: Optional[str] = None
_expires_at: float = 0.0


def _login() -> str:
    if not (IAM_URL and SERVICE_ACCOUNT_EMAIL and SERVICE_ACCOUNT_PASSWORD):
        raise RuntimeError(
            "IAM_URL, SERVICE_ACCOUNT_EMAIL, SERVICE_ACCOUNT_PASSWORD must all be set"
        )
    resp = requests.post(
        f"{IAM_URL}/login",
        json={"email": SERVICE_ACCOUNT_EMAIL, "password": SERVICE_ACCOUNT_PASSWORD},
        timeout=LOGIN_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    return resp.json()["auth_token"]


def get_service_token(force_refresh: bool = False) -> str:
    global _cached_token, _expires_at
    with _lock:
        now = time.time()
        if (
            force_refresh
            or _cached_token is None
            or now >= _expires_at - REFRESH_BUFFER_SECONDS
        ):
            _cached_token = _login()
            _expires_at = now + TOKEN_LIFETIME_SECONDS
        return _cached_token


def auth_header() -> dict:
    return {"Authorization": f"Bearer {get_service_token()}"}
