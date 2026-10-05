from datetime import datetime
from typing import TYPE_CHECKING
from app.database import Base
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
if TYPE_CHECKING:
    from app.auth.models import User


class ShortURL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_url: Mapped[str] = mapped_column(String, nullable=False)
    short_code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    click_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    owner: Mapped["User"] = relationship(back_populates="urls")
    clicks:Mapped["URLClick"]=relationship(back_populates="url")


class URLClick(Base):
    __tablename__="clicks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    short_code:Mapped[str]=mapped_column(ForeignKey("urls.short_code"),nullable=False,index=True)
    clicked_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    ip_address:Mapped[str | None]=mapped_column(String(50),nullable=True)
    country:Mapped[str|None]=mapped_column(String(100),nullable=True)

    url:Mapped["ShortURL"]=relationship(back_populates="clicks")


