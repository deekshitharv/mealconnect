from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.meal import LocationMini, ProviderMini, as_utc


class ReservationCreate(BaseModel):
    meal_id: int = Field(gt=0, examples=[1])
    quantity: int = Field(gt=0, le=100, examples=[2])


class ReservationMeal(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    image_url: str | None
    available_until: datetime
    status: str
    location: LocationMini
    provider: ProviderMini


class ReservationUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity: int
    status: str  # what is stored in the database
    reserved_at: datetime
    collected_at: datetime | None
    cancelled_at: datetime | None
    meal: ReservationMeal
    user: ReservationUser

    @computed_field
    @property
    def display_status(self) -> str:
        """Calculated: a RESERVED reservation whose pickup time has passed shows as EXPIRED."""
        if self.status == "RESERVED" and as_utc(self.meal.available_until) <= datetime.now(timezone.utc):
            return "EXPIRED"
        return self.status

    @computed_field
    @property
    def is_active(self) -> bool:
        """True while it can still be cancelled or collected."""
        return self.display_status == "RESERVED"


class ReservationList(BaseModel):
    items: list[ReservationOut]
    page: int
    limit: int
    total: int
    total_pages: int