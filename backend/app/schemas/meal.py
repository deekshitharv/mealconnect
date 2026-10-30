from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
    model_validator,
)

EXPIRING_SOON_HOURS = 2


def as_utc(value: datetime) -> datetime:
    """If a time has no timezone, assume UTC, so comparisons never crash."""
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class MealBase(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)] = Field(
        examples=["Veg fried rice"]
    )
    description: str | None = Field(default=None, max_length=1000)
    category_id: int = Field(gt=0, examples=[1])
    location_id: int = Field(gt=0, examples=[1])
    available_from: datetime
    available_until: datetime
    image_url: str | None = Field(default=None, max_length=500)

    @field_validator("available_from", "available_until")
    @classmethod
    def make_timezone_aware(cls, value: datetime) -> datetime:
        return as_utc(value)

    @field_validator("description")
    @classmethod
    def blank_description_is_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("image_url")
    @classmethod
    def check_image_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        if not value.startswith(("http://", "https://")):
            raise ValueError("image_url must start with http:// or https://")
        return value

    @model_validator(mode="after")
    def check_time_window(self):
        if self.available_until <= self.available_from:
            raise ValueError("available_until must be after available_from")
        return self


class MealCreate(MealBase):
    quantity: int = Field(gt=0, le=1000, examples=[10])

    @model_validator(mode="after")
    def must_end_in_future(self):
        if self.available_until <= datetime.now(timezone.utc):
            raise ValueError("available_until must be in the future")
        return self


class MealUpdate(MealBase):
    """PUT replaces the meal's details. Quantity 0 is allowed here (closes the listing)."""

    quantity: int = Field(ge=0, le=1000, examples=[10])
    # Providers can only switch between these two by hand.
    status: Literal["AVAILABLE", "UNAVAILABLE"] | None = None


class CategoryMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class LocationMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    address: str
    city: str


class ProviderMini(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class MealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    quantity: int
    available_from: datetime
    available_until: datetime
    status: str  # what is stored in the database
    image_url: str | None
    created_at: datetime
    updated_at: datetime
    category: CategoryMini
    location: LocationMini
    provider: ProviderMini

    @computed_field
    @property
    def display_status(self) -> str:
        """Calculated, not stored: an AVAILABLE meal past its end time shows as EXPIRED."""
        if self.status == "AVAILABLE" and as_utc(self.available_until) <= datetime.now(timezone.utc):
            return "EXPIRED"
        return self.status

    @computed_field
    @property
    def expiring_soon(self) -> bool:
        """True if still available and ending within 2 hours."""
        if self.display_status != "AVAILABLE":
            return False
        remaining = as_utc(self.available_until) - datetime.now(timezone.utc)
        return remaining <= timedelta(hours=EXPIRING_SOON_HOURS)


class MealList(BaseModel):
    items: list[MealOut]
    page: int
    limit: int
    total: int
    total_pages: int