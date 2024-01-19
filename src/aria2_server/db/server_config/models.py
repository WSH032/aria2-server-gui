import secrets

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from aria2_server.db.base._models import Base

__all__ = ("ServerConfig",)


class ServerConfig(Base):
    __tablename__ = "server_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    secret_token: Mapped[str] = mapped_column(
        String(length=43), nullable=False, default=secrets.token_urlsafe
    )
