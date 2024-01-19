from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyBaseAccessTokenTableUUID,
)

from aria2_server.db.base._models import Base

__all__ = ("AccessToken",)


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass
