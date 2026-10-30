from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class CategoryIn(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=50)] = Field(
        examples=["Lunch"]
    )
    description: str | None = Field(default=None, max_length=255, examples=["Midday meals"])


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    