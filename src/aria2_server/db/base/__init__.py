# ruff: noqa: F401
# pyright: reportUnusedImport=false

# NOTE: import `fastapi_users.db` before `fastapi_users_db_sqlalchemy`
# to avoid circular import
import fastapi_users.db

# Just import all the models here to initialize them
import aria2_server.db.access_token.models
import aria2_server.db.server_config.models
import aria2_server.db.user.models
from aria2_server.db.base._models import Base

# Don't export any models except `Base` here,
# let user import them from `aria2_server.db.<table>.models` instead
__all__ = ("Base",)
