from  typing import TypedDict
from uuid import UUID
from datetime import datetime

class JwtPayload(TypedDict):
    user_id: UUID
    exp: datetime | None = None
    email: str