import math
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.session import get_db
from app.dependencies.roles import require_admin
from app.models.meal import Meal
from app.models.reservation import Reservation
from app.models.user import User
from app.schemas.admin import AdminStats, UserAdminList, UserAdminOut

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])
logger = get_logger("admin")

ADMIN_ERRORS = {401: {"description": "Not logged in"}, 403: {"description": "ADMIN only"}}


def _count(db: Session, stmt) -> int:
    return db.scalar(stmt) or 0


@router.get("/stats", response_model=AdminStats, summary="System statistics (ADMIN)", responses=ADMIN_ERRORS)
def system_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    return AdminStats(
        total_users=_count(db, select(func.count()).select_from(User).where(User.role == "USER")),
        total_providers=_count(db, select(func.count()).select_from(User).where(User.role == "PROVIDER")),
        total_meals=_count(db, select(func.count()).select_from(Meal)),
        active_meals=_count(
            db,
            select(func.count()).select_from(Meal).where(Meal.status == "AVAILABLE", Meal.available_until > now),
        ),
        total_reservations=_count(db, select(func.count()).select_from(Reservation)),
        collected_reservations=_count(
            db, select(func.count()).select_from(Reservation).where(Reservation.status == "COLLECTED")
        ),
    )


@router.get(
    "/users",
    response_model=UserAdminList,
    summary="List users and providers (ADMIN). Use role=PROVIDER to see providers only",
    responses=ADMIN_ERRORS,
)
def list_users(
    role: Literal["USER", "PROVIDER", "ADMIN"] | None = Query(None),
    search: str | None = Query(None, max_length=100, description="Name or email"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(or_(User.name.ilike(pattern), User.email.ilike(pattern)))

    total = _count(db, select(func.count()).select_from(stmt.subquery()))
    users = db.scalars(stmt.order_by(User.id).offset((page - 1) * limit).limit(limit)).all()
    return UserAdminList(
        items=[UserAdminOut.model_validate(u) for u in users],
        page=page,
        limit=limit,
        total=total,
        total_pages=math.ceil(total / limit) if total else 0,
    )


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user and everything they own (ADMIN)",
    responses={**ADMIN_ERRORS, 404: {"description": "User not found"}, 409: {"description": "Cannot delete yourself"}},
)
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if user_id == admin.id:
        raise HTTPException(status.HTTP_409_CONFLICT, "You cannot delete your own account")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    db.delete(user)
    db.commit()
    logger.info("User deleted: id=%s by admin_id=%s", user_id, admin.id)