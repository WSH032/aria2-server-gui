import uuid

from fastapi_users import schemas

__all__ = ("UserRead", "UserCreate", "UserUpdate")


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
