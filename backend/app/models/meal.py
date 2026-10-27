from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import MealStatus, sql_values

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.location import Location
    from app.models.reservation import Reservation
    from app.models.user import User


class Meal(Base):
    __tablename__ = "meals"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_meals_quantity_not_negative"),
        CheckConstraint("available_until > available_from", name="ck_meals_time_window"),
        CheckConstraint(f"status IN ({sql_values(MealStatus)})", name="ck_meals_status"),
        Index("ix_meals_status_until", "status", "available_until"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys: these link a meal to its provider, category and location.
    provider_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="RESTRICT"), index=True)

    name: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)  # portions still available
    available_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    available_until: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(
        String(20), default=MealStatus.AVAILABLE.value, server_default=MealStatus.AVAILABLE.value
    )
    image_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    provider: Mapped["User"] = relationship(back_populates="meals")
    category: Mapped["Category"] = relationship(back_populates="meals")
    location: Mapped["Location"] = relationship(back_populates="meals")
    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="meal", cascade="all, delete-orphan", passive_deletes=True
    )