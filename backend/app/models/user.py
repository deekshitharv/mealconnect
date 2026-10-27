from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import UserRole, sql_values

if TYPE_CHECKING:
    from app.models.meal import Meal
    from app.models.reservation import Reservation


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(f"role IN ({sql_values(UserRole)})", name="ck_users_role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))  # never the plain password
    role: Mapped[str] = mapped_column(
        String(20), default=UserRole.USER.value, server_default=UserRole.USER.value
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # A provider can create many meals; a user can make many reservations.
    meals: Mapped[list["Meal"]] = relationship(
        back_populates="provider", cascade="all, delete-orphan", passive_deletes=True
    )
    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )