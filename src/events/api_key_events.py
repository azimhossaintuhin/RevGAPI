from sqlalchemy import event
from src.models.users import User, ApiKey


@event.listens_for(User, "after_insert")
def create_api_key(mapper, connection, target):
    connection.execute(
        ApiKey.__table__.insert().values(
            user_id=target.id
        )
    )
    print(f"API key created for user: {target.id}")