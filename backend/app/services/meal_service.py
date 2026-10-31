import math
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import Session, contains_eager, joinedload

from app.core.logging_config import get_logger
from app.models.category import Category
from app.models.location import Location
from app.models.meal import Meal
from app.models.reservation import Reservation
from app.models.user import User
from app.schemas.meal import MealCreate, MealUpdate

logger = get_logger("meals")

LOAD_RELATIONS = [joinedload(Meal.provider), joinedload(Meal.category), joinedload(Meal.location)]


def _like_pattern(text: str) -> str:
    """Escape % and _ so user text is searched literally, then wrap for 'contains'."""
    cleaned = text.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{cleaned}%"


def list_meals(
    db: Session,
    *,
    search: str | None,
    category: str | None,
    location: str | None,
    provider_id: int | None,
    status_filter: str | None,
    sort: str,
    page: int,
    limit: int,
) -> tuple[list[Meal], int]:
    now = datetime.now(timezone.utc)
    stmt = select(Meal).join(Meal.category).join(Meal.location)

    if search and search.strip():
        pattern = _like_pattern(search)
        stmt = stmt.where(
            or_(Meal.name.ilike(pattern, escape="\\"), Meal.description.ilike(pattern, escape="\\"))
        )
    if category and category.strip():
        stmt = stmt.where(func.lower(Category.name) == category.strip().lower())
    if location and location.strip():
        pattern = _like_pattern(location)
        stmt = stmt.where(
            or_(Location.city.ilike(pattern, escape="\\"), Location.name.ilike(pattern, escape="\\"))
        )
    if provider_id:
        stmt = stmt.where(Meal.provider_id == provider_id)

    # Status filter uses the *effective* status, so expiry is respected.
    if status_filter == "AVAILABLE":
        stmt = stmt.where(Meal.status == "AVAILABLE", Meal.available_until > now)
    elif status_filter == "EXPIRED":
        stmt = stmt.where(
            or_(Meal.status == "EXPIRED", and_(Meal.status == "AVAILABLE", Meal.available_until <= now))
        )
    elif status_filter:
        stmt = stmt.where(Meal.status == status_filter)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    if sort == "expiry":
        # Soonest-ending first, with already-ended meals pushed to the bottom.
        order = [case((Meal.available_until <= now, 1), else_=0), Meal.available_until.asc(), Meal.id]
    elif sort == "quantity":
        order = [Meal.quantity.desc(), Meal.id]
    else:  # newest
        order = [Meal.created_at.desc(), Meal.id.desc()]

    stmt = (
        stmt.options(contains_eager(Meal.category), contains_eager(Meal.location), joinedload(Meal.provider))
        .order_by(*order)
        .offset((page - 1) * limit)
        .limit(limit)
    )
    meals = list(db.scalars(stmt).unique().all())
    return meals, total


def total_pages(total: int, limit: int) -> int:
    return math.ceil(total / limit) if total else 0


def get_meal_or_404(db: Session, meal_id: int) -> Meal:
    meal = db.get(Meal, meal_id, options=LOAD_RELATIONS)
    if meal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meal not found")
    return meal


def ensure_can_modify(meal: Meal, user: User) -> None:
    """Admins can change any meal. Providers only their own."""
    if user.role != "ADMIN" and meal.provider_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only modify your own meals")


def _ensure_category_and_location_exist(db: Session, category_id: int, location_id: int) -> None:
    if db.get(Category, category_id) is None:
        raise HTTPException(422, "Category does not exist")
    if db.get(Location, location_id) is None:
        raise HTTPException(422, "Location does not exist")


def _sync_status(meal: Meal, requested: str | None) -> None:
    if requested == "UNAVAILABLE" or (requested is None and meal.status == "UNAVAILABLE"):
        meal.status = "UNAVAILABLE"
    elif meal.quantity == 0:
        meal.status = "FULLY_RESERVED"
    else:
        meal.status = "AVAILABLE"


def create_meal(db: Session, provider: User, payload: MealCreate) -> Meal:
    _ensure_category_and_location_exist(db, payload.category_id, payload.location_id)
    meal = Meal(provider_id=provider.id, status="AVAILABLE", **payload.model_dump())
    db.add(meal)
    db.commit()
    logger.info("Meal created: id=%s provider_id=%s", meal.id, provider.id)
    return get_meal_or_404(db, meal.id)


def update_meal(db: Session, meal: Meal, payload: MealUpdate, actor: User) -> Meal:
    _ensure_category_and_location_exist(db, payload.category_id, payload.location_id)
    for field, value in payload.model_dump(exclude={"status"}).items():
        setattr(meal, field, value)
    _sync_status(meal, payload.status)
    db.commit()
    logger.info("Meal updated: id=%s by user_id=%s", meal.id, actor.id)
    return get_meal_or_404(db, meal.id)


def delete_meal(db: Session, meal: Meal, actor: User) -> None:
    if actor.role != "ADMIN":
        active = db.scalar(
            select(func.count())
            .select_from(Reservation)
            .where(Reservation.meal_id == meal.id, Reservation.status == "RESERVED")
        )
        if active:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "This meal has active reservations. Collect or cancel them first.",
            )
    meal_id = meal.id
    db.delete(meal)
    db.commit()
    logger.info("Meal deleted: id=%s by user_id=%s", meal_id, actor.id)