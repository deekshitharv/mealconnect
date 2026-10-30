from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.roles import require_provider
from app.models.meal import Meal
from app.models.reservation import Reservation
from app.models.user import User
from app.schemas.admin import ProviderStats

router = APIRouter(prefix="/api/v1/provider", tags=["Provider"])


@router.get(
    "/stats",
    response_model=ProviderStats,
    summary="Dashboard statistics for the logged-in provider (PROVIDER)",
    responses={401: {"description": "Not logged in"}, 403: {"description": "PROVIDER only"}},
)
def provider_stats(db: Session = Depends(get_db), provider: User = Depends(require_provider)):
    now = datetime.now(timezone.utc)
    mine = Meal.provider_id == provider.id

    def count(stmt) -> int:
        return db.scalar(stmt) or 0

    reservations_on_mine = (
        select(func.count()).select_from(Reservation).join(Meal, Reservation.meal_id == Meal.id).where(mine)
    )
    return ProviderStats(
        active_listings=count(
            select(func.count()).select_from(Meal).where(mine, Meal.status == "AVAILABLE", Meal.available_until > now)
        ),
        expired_listings=count(
            select(func.count()).select_from(Meal).where(
                mine,
                or_(Meal.status == "EXPIRED", and_(Meal.status == "AVAILABLE", Meal.available_until <= now)),
            )
        ),
        total_reservations=count(reservations_on_mine),
        collected_reservations=count(reservations_on_mine.where(Reservation.status == "COLLECTED")),
    )
