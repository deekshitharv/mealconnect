from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_provider_or_admin
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationList, ReservationOut
from app.services import reservation_service as service

router = APIRouter(prefix="/api/v1/reservations", tags=["Reservations"])

AUTH_ERRORS = {401: {"description": "Missing, invalid or expired token"}}
StatusFilter = Literal["RESERVED", "COLLECTED", "CANCELLED"]


def _page_response(reservations, total, page, limit) -> ReservationList:
    return ReservationList(
        items=[ReservationOut.model_validate(r) for r in reservations],
        page=page,
        limit=limit,
        total=total,
        total_pages=service.total_pages(total, limit),
    )


@router.post(
    "",
    response_model=ReservationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Reserve portions of a meal",
    responses={
        **AUTH_ERRORS,
        403: {"description": "You cannot reserve your own meal"},
        404: {"description": "Meal not found"},
        409: {"description": "Meal expired, fully reserved, not yet available, or not enough portions"},
        422: {"description": "Invalid quantity"},
    },
)
def create_reservation(
    payload: ReservationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """Checks the meal, creates the reservation and lowers the meal's quantity in one transaction."""
    return ReservationOut.model_validate(service.create_reservation(db, user, payload))


@router.get("/my", response_model=ReservationList, summary="My reservations (current and history)", responses=AUTH_ERRORS)
def my_reservations(
    status_filter: StatusFilter | None = Query(None, alias="status", description="Filter by stored status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = service.list_reservations(db, user_id=user.id, status_filter=status_filter, page=page, limit=limit)
    return _page_response(items, total, page, limit)


@router.get(
    "/provider",
    response_model=ReservationList,
    summary="Reservations on my meals (PROVIDER) or all reservations (ADMIN)",
    responses={**AUTH_ERRORS, 403: {"description": "PROVIDER or ADMIN only"}},
)
def provider_reservations(
    status_filter: StatusFilter | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    user: User = Depends(require_provider_or_admin),
):
    provider_id = None if user.role == "ADMIN" else user.id
    items, total = service.list_reservations(
        db, provider_id=provider_id, status_filter=status_filter, page=page, limit=limit
    )
    return _page_response(items, total, page, limit)


@router.get(
    "/{reservation_id}",
    response_model=ReservationOut,
    summary="Get one reservation",
    responses={**AUTH_ERRORS, 403: {"description": "Not your reservation"}, 404: {"description": "Not found"}},
)
def get_reservation(reservation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reservation = service.get_reservation_or_404(db, reservation_id)
    service.ensure_can_view(reservation, user)
    return ReservationOut.model_validate(reservation)


@router.put(
    "/{reservation_id}/cancel",
    response_model=ReservationOut,
    summary="Cancel a reservation (owner or ADMIN)",
    responses={
        **AUTH_ERRORS,
        403: {"description": "Not your reservation"},
        404: {"description": "Not found"},
        409: {"description": "Already collected or cancelled, or pickup time has passed"},
    },
)
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Returns the reserved portions to the meal."""
    return ReservationOut.model_validate(service.cancel_reservation(db, reservation_id, user))


@router.put(
    "/{reservation_id}/collect",
    response_model=ReservationOut,
    summary="Mark a reservation as collected (the meal's PROVIDER or ADMIN)",
    responses={
        **AUTH_ERRORS,
        403: {"description": "Not the meal's provider"},
        404: {"description": "Not found"},
        409: {"description": "Already collected or cancelled, or pickup time has passed"},
    },
)
def collect_reservation(reservation_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ReservationOut.model_validate(service.collect_reservation(db, reservation_id, user))