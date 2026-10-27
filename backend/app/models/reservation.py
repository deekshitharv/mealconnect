from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import ReservationStatus, sql_values

if TYPE_CHECKING:
    from app.models.meal import Meal
    from app.models.user import User


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_reservations_quantity_positive"),
        CheckConstraint(
            f"status IN ({sql_values(ReservationStatus)})", name="ck_reservations_status"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.id", ondelete="CASCADE"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(20),
        default=ReservationStatus.RESERVED.value,
        server_default=ReservationStatus.RESERVED.value,
    )
    reserved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="reservations")
    meal: Mapped["Meal"] = relationship(back_populates="reservations")