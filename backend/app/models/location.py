from typing import TYPE_CHECKING

from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.meal import Meal


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100), index=True)
    latitude: Mapped[float | None] = mapped_column(Float)   # optional
    longitude: Mapped[float | None] = mapped_column(Float)  # optional

    meals: Mapped[list["Meal"]] = relationship(back_populates="location")