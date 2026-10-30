from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.session import get_db
from app.dependencies.roles import require_admin, require_provider_or_admin
from app.models.location import Location
from app.models.meal import Meal
from app.schemas.location import LocationIn, LocationOut

router = APIRouter(prefix="/api/v1/locations", tags=["Locations"])
logger = get_logger("locations")

AUTH_ERRORS = {401: {"description": "Not logged in"}, 403: {"description": "Role not allowed"}}


def _get_or_404(db: Session, location_id: int) -> Location:
    location = db.get(Location, location_id)
    if location is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Location not found")
    return location


@router.get("", response_model=list[LocationOut], summary="List locations (public)")
def list_locations(db: Session = Depends(get_db)):
    return db.scalars(select(Location).order_by(Location.city, Location.name)).all()


@router.post(
    "", response_model=LocationOut, status_code=status.HTTP_201_CREATED,
    summary="Create a location (PROVIDER or ADMIN)", responses=AUTH_ERRORS,
)
def create_location(payload: LocationIn, db: Session = Depends(get_db), user=Depends(require_provider_or_admin)):
    location = Location(**payload.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    logger.info("Location created: id=%s by user_id=%s", location.id, user.id)
    return location


@router.put(
    "/{location_id}", response_model=LocationOut, summary="Update a location (ADMIN)",
    responses={**AUTH_ERRORS, 404: {"description": "Not found"}},
)
def update_location(location_id: int, payload: LocationIn, db: Session = Depends(get_db), admin=Depends(require_admin)):
    location = _get_or_404(db, location_id)
    for field, value in payload.model_dump().items():
        setattr(location, field, value)
    db.commit()
    db.refresh(location)
    logger.info("Location updated: id=%s by admin_id=%s", location.id, admin.id)
    return location


@router.delete(
    "/{location_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a location (ADMIN)",
    responses={**AUTH_ERRORS, 404: {"description": "Not found"}, 409: {"description": "Location is in use"}},
)
def delete_location(location_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    location = _get_or_404(db, location_id)
    in_use = db.scalar(select(func.count()).select_from(Meal).where(Meal.location_id == location_id))
    if in_use:
        raise HTTPException(status.HTTP_409_CONFLICT, "This location is used by meals and cannot be deleted")
    db.delete(location)
    db.commit()
    logger.info("Location deleted: id=%s by admin_id=%s", location_id, admin.id)