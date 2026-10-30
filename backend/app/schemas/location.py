from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Text100 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]


class LocationIn(BaseModel):
    name: Text100 = Field(examples=["Green Leaf Cafe"])
    address: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)] = Field(
        examples=["12 MG Road"]
    )
    city: Text100 = Field(examples=["Bangalore"])
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    city: str
    latitude: float | None
    longitude: float | None