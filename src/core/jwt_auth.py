from datetime import datetime, timedelta, timezone
from uuid import UUID

from decouple import config
from fastapi import HTTPException, status
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from src.prototypes.jwt_payload import JwtPayload

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: JwtPayload):
    to_encode = data.copy()
    user_id = to_encode.get("user_id")
    if isinstance(user_id, UUID):
        to_encode["user_id"] = str(user_id)
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> JwtPayload:
    try:
        payload: JwtPayload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
