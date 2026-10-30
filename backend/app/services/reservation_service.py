import math
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.logging_config import get_logger
from app.models.meal import Meal
from app.models.reservation import Reservation
from app.models.user import User
from app.schemas.meal import as_utc
from app.schemas.reservation import ReservationCreate

logger = get_logger("reservations")

LOAD_RELATIONS = [
    joinedload(Reservation.user),
    joinedload(Reservation.meal).joinedload(Meal.location),
    joinedload(Reservation.meal).joinedload(Meal.provider),
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _window_open(meal: Meal) -> bool:
    """True while the pickup time has not ended."""
    return as_utc(meal.available_until) > _now()


def total_pages(total: int, limit: int) -> int:
    return math.ceil(total / limit) if total else 0


def get_reservation_or_404(db: Session, reservation_id: int) -> Reservation:
    reservation = db.get(Reservation, reservation_id, options=LOAD_RELATIONS)
    if reservation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reservation not found")
    return reservation


def ensure_can_view(reservation: Reservation, user: User) -> None:
    """Allowed: the person who reserved, the meal's provider, or an admin."""
    if user.role == "ADMIN":
        return
    if reservation.user_id == user.id or reservation.meal.provider_id == user.id:
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only view your own reservations")


def _lock_reservation(db: Session, reservation_id: int) -> Reservation:
    """SELECT ... FOR UPDATE: nobody else can change this row until we commit."""
    reservation = db.scalar(select(Reservation).where(Reservation.id == reservation_id).with_for_update())
    if reservation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reservation not found")
    return reservation


def create_reservation(db: Session, user: User, payload: ReservationCreate) -> Reservation:
    # Lock the meal row first. If two people reserve at the same moment,
    # the second one waits here until the first has committed, then sees the new quantity.
    meal = db.scalar(select(Meal).where(Meal.id == payload.meal_id).with_for_update())
    if meal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Meal not found")

    if meal.provider_id == user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You cannot reserve your own meal")
    if meal.status == "UNAVAILABLE":
        raise HTTPException(status.HTTP_409_CONFLICT, "This meal is no longer available")
    if not _window_open(meal):
        raise HTTPException(status.HTTP_409_CONFLICT, "This meal has expired")
    if as_utc(meal.available_from) > _now():
        raise HTTPException(status.HTTP_409_CONFLICT, "This meal is not available yet")
    if meal.status == "FULLY_RESERVED" or meal.quantity == 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "This meal is fully reserved")
    if payload.quantity > meal.quantity:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Only {meal.quantity} portion(s) left")

    reservation = Reservation(
        user_id=user.id, meal_id=meal.id, quantity=payload.quantity, status="RESERVED"
    )
    meal.quantity -= payload.quantity
    if meal.quantity == 0:
        meal.status = "FULLY_RESERVED"

    db.add(reservation)
    db.commit()  # the reservation AND the new quantity are saved together, or not at all
    logger.info(
        "Reservation created: id=%s user_id=%s meal_id=%s qty=%s",
        reservation.id, user.id, meal.id, payload.quantity,
    )
    return get_reservation_or_404(db, reservation.id)


def cancel_reservation(db: Session, reservation_id: int, actor: User) -> Reservation:
    reservation = _lock_reservation(db, reservation_id)

    if actor.role != "ADMIN" and reservation.user_id != actor.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only cancel your own reservations")
    if reservation.status != "RESERVED":
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"This reservation is already {reservation.status.lower()}"
        )

    meal = db.scalar(select(Meal).where(Meal.id == reservation.meal_id).with_for_update())
    if not _window_open(meal):
        raise HTTPException(status.HTTP_409_CONFLICT, "The pickup time for this meal has passed")

    reservation.status = "CANCELLED"
    reservation.cancelled_at = _now()
    meal.quantity += reservation.quantity  # give the portions back
    if meal.status == "FULLY_RESERVED":
        meal.status = "AVAILABLE"

    db.commit()
    logger.info("Reservation cancelled: id=%s by user_id=%s", reservation_id, actor.id)
    return get_reservation_or_404(db, reservation_id)


def collect_reservation(db: Session, reservation_id: int, actor: User) -> Reservation:
    reservation = _lock_reservation(db, reservation_id)
    meal = db.get(Meal, reservation.meal_id)

    if actor.role != "ADMIN" and meal.provider_id != actor.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the meal's provider can mark it as collected")
    if reservation.status != "RESERVED":
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"This reservation is already {reservation.status.lower()}"
        )
    if not _window_open(meal):
        raise HTTPException(status.HTTP_409_CONFLICT, "The pickup time for this meal has passed")

    reservation.status = "COLLECTED"
    reservation.collected_at = _now()
    db.commit()
    logger.info("Reservation collected: id=%s by user_id=%s", reservation_id, actor.id)
    return get_reservation_or_404(db, reservation_id)


def list_reservations(
    db: Session,
    *,
    user_id: int | None = None,
    provider_id: int | None = None,
    status_filter: str | None = None,
    page: int,
    limit: int,
) -> tuple[list[Reservation], int]:
    """user_id = only that user's reservations. provider_id = reservations on that provider's meals.
    Neither = everything (used for admins)."""
    stmt = select(Reservation)
    if user_id is not None:
        stmt = stmt.where(Reservation.user_id == user_id)
    if provider_id is not None:
        stmt = stmt.where(Reservation.meal_id.in_(select(Meal.id).where(Meal.provider_id == provider_id)))
    if status_filter:
        stmt = stmt.where(Reservation.status == status_filter)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = (
        stmt.options(*LOAD_RELATIONS)
        .order_by(Reservation.reserved_at.desc(), Reservation.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    return list(db.scalars(stmt).unique().all()), total
