from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from aria2_server.db.base._models import Base

__all__ = ("User",)


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
