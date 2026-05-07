import os

import uvicorn
from fastapi import FastAPI

from db import Base, engine
from pdmodels.login_req import LoginReq
from pdmodels.token_req import TokenReq
from pdmodels.user_req import UserReq
from resources.user import User

app = FastAPI(title="IAM Service", version="0.1.0")
Base.metadata.create_all(engine)


@app.post("/users")
def register_user(u_req: UserReq):
    return User.register(u_req)


@app.post("/login")
def login(login_req: LoginReq):
    return User.login(login_req)


@app.post("/validate")
def validate_token(token_req: TokenReq):
    return User.validate(token_req)


@app.get("/users/{u_id}")
def get_user(u_id: str):
    return User.get(u_id)


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
