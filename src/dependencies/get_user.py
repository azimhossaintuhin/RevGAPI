from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.core.jwt_auth import verify_token
from src.prototypes.jwt_payload import JwtPayload
from uuid import UUID
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> UUID:
    payload: JwtPayload = verify_token(token)
    user_id: UUID = payload["user_id"]
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user_id

CurrentUserID = Annotated[UUID, Depends(get_current_user)]