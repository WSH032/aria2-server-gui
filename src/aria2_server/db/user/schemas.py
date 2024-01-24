import uuid

from fastapi_users import schemas

__all__ = ("UserCreate", "UserRead", "UserUpdate")


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
