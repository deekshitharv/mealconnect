from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminStats(BaseModel):
    total_users: int        # accounts with role USER
    total_providers: int    # accounts with role PROVIDER
    total_meals: int
    active_meals: int       # AVAILABLE and not yet expired
    total_reservations: int
    collected_reservations: int


class ProviderStats(BaseModel):
    active_listings: int
    expired_listings: int
    total_reservations: int
    collected_reservations: int


class UserAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    created_at: datetime


class UserAdminList(BaseModel):
    items: list[UserAdminOut]
    page: int
    limit: int
    total: int
    total_pages: int
    