import secrets
from sqlalchemy import select
from sqlalchemy import event
from src.models.users import User, UserToken , TokenType
from sqlalchemy.orm import Session

@event.listens_for(User, "after_insert")
def create_token(mapper, connection:Session, target:User):

    while True:
        token = f"{secrets.randbelow(10000):04d}"

        exists = connection.execute(
            select(UserToken.id)
            .where(UserToken.token == token)
        ).scalar_one_or_none()

        if not exists:
            break

    connection.execute(
        UserToken.__table__.insert().values(
            user_id=target.id,
            token_type=TokenType.ep,
            token=token,
        )
    )