import os
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext

from daos.user_dao import UserDAO
from db import Session
from pdmodels.login_req import LoginReq
from pdmodels.login_res import LoginRes
from pdmodels.token_req import TokenReq
from pdmodels.user_req import UserReq
from pdmodels.user_res import UserRes

# JWT configuration — read from env, with development-only fallback
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-insecure-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = int(os.environ.get("JWT_EXPIRES_MINUTES", "60"))

# bcrypt password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_access_token(user: UserDAO) -> tuple[str, int]:
    """Returns (encoded_jwt, expires_in_seconds)."""
    expires_delta = timedelta(minutes=JWT_EXPIRES_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": user.id,           # JWT standard: subject = user id
        "username": user.username,
        "role": user.role,
        "exp": expire,            # JWT standard: expiry timestamp
        "iat": datetime.now(timezone.utc),  # JWT standard: issued-at
    }
    encoded = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded, JWT_EXPIRES_MINUTES * 60


class User:
    @staticmethod
    def register(u_req: UserReq):
        session = Session()
        try:
            # Uniqueness check (BigQuery doesn't enforce unique constraints)
            existing = session.query(UserDAO).filter(UserDAO.username == u_req.username).first()
            if existing:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"Username '{u_req.username}' already taken"}),
                    status_code=status.HTTP_409_CONFLICT,
                )

            user = UserDAO(
                id=f"user_{uuid.uuid4().hex[:12]}",
                username=u_req.username,
                email=u_req.email,
                password_hash=_hash_password(u_req.password),
                role=u_req.role.value,
                full_name=u_req.full_name,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            response = UserRes.model_validate(user)
            return JSONResponse(
                content=jsonable_encoder(response.model_dump()),
                status_code=status.HTTP_201_CREATED,
            )
        finally:
            session.close()

    @staticmethod
    def login(login_req: LoginReq):
        session = Session()
        try:
            user = session.query(UserDAO).filter(UserDAO.username == login_req.username).first()
            if not user or not _verify_password(login_req.password, user.password_hash):
                # Same response for "wrong username" vs "wrong password" — security best practice
                return JSONResponse(
                    content=jsonable_encoder({"message": "Invalid username or password"}),
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            token, expires_in = _create_access_token(user)
            response = LoginRes(
                access_token=token,
                expires_in=expires_in,
                user_id=user.id,
                username=user.username,
                role=user.role,
            )
            return JSONResponse(
                content=jsonable_encoder(response.model_dump()),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()

    @staticmethod
    def validate(token_req: TokenReq):
        """Validate a JWT and return its decoded claims.
        Other services SHOULD validate locally using the shared secret.
        This endpoint exists for completeness and debugging."""
        try:
            payload = jwt.decode(token_req.token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return JSONResponse(
                content=jsonable_encoder({
                    "valid": True,
                    "user_id": payload.get("sub"),
                    "username": payload.get("username"),
                    "role": payload.get("role"),
                    "expires_at": payload.get("exp"),
                }),
                status_code=status.HTTP_200_OK,
            )
        except JWTError as e:
            return JSONResponse(
                content=jsonable_encoder({"valid": False, "reason": str(e)}),
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    @staticmethod
    def get(u_id: str):
        session = Session()
        try:
            user = session.query(UserDAO).filter(UserDAO.id == u_id).first()
            if not user:
                return JSONResponse(
                    content=jsonable_encoder({"message": f"No user with id {u_id}"}),
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            response = UserRes.model_validate(user)
            return JSONResponse(
                content=jsonable_encoder(response.model_dump()),
                status_code=status.HTTP_200_OK,
            )
        finally:
            session.close()
