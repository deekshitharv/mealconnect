from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.roles import require_provider, require_provider_or_admin
from app.models.user import User
from app.schemas.meal import MealCreate, MealList, MealOut, MealUpdate
from app.services import meal_service

router = APIRouter(prefix="/api/v1/meals", tags=["Meals"])

AUTH_ERRORS = {
    401: {"description": "Missing, invalid or expired token"},
    403: {"description": "Your role or ownership does not allow this"},
}


@router.get("", response_model=MealList, summary="List meals (public) with search, filters, sorting and pagination")
def list_meals(
    search: str | None = Query(None, max_length=100, description="Text to find in name or description"),
    category: str | None = Query(None, max_length=50, description="Category name, e.g. Lunch"),
    location: str | None = Query(None, max_length=100, description="City or location name, e.g. Bangalore"),
    status_filter: Literal["AVAILABLE", "FULLY_RESERVED", "EXPIRED", "UNAVAILABLE"] | None = Query(
        None, alias="status", description="Meal status"
    ),
    sort: Literal["newest", "expiry", "quantity"] = Query("newest", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number, starting at 1"),
    limit: int = Query(10, ge=1, le=50, description="Items per page (max 50)"),
    db: Session = Depends(get_db),
):
    meals, total = meal_service.list_meals(
        db,
        search=search,
        category=category,
        location=location,
        status_filter=status_filter,
        sort=sort,
        page=page,
        limit=limit,
    )
    return MealList(
        items=[MealOut.model_validate(m) for m in meals],
        page=page,
        limit=limit,
        total=total,
        total_pages=meal_service.total_pages(total, limit),
    )


@router.post(
    "",
    response_model=MealOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a meal (PROVIDER only)",
    responses={**AUTH_ERRORS, 422: {"description": "Invalid input"}},
)
def create_meal(payload: MealCreate, db: Session = Depends(get_db), provider: User = Depends(require_provider)):
    meal = meal_service.create_meal(db, provider, payload)
    return MealOut.model_validate(meal)


@router.get("/{meal_id}", response_model=MealOut, summary="Get one meal (public)", responses={404: {"description": "Meal not found"}})
def get_meal(meal_id: int, db: Session = Depends(get_db)):
    return MealOut.model_validate(meal_service.get_meal_or_404(db, meal_id))


@router.put(
    "/{meal_id}",
    response_model=MealOut,
    summary="Update a meal (owner or ADMIN)",
    responses={**AUTH_ERRORS, 404: {"description": "Meal not found"}, 422: {"description": "Invalid input"}},
)
def update_meal(
    meal_id: int,
    payload: MealUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_provider_or_admin),
):
    meal = meal_service.get_meal_or_404(db, meal_id)
    meal_service.ensure_can_modify(meal, user)
    updated = meal_service.update_meal(db, meal, payload, user)
    return MealOut.model_validate(updated)


@router.delete(
    "/{meal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a meal (owner or ADMIN)",
    responses={**AUTH_ERRORS, 404: {"description": "Meal not found"}, 409: {"description": "Meal has active reservations"}},
)
def delete_meal(meal_id: int, db: Session = Depends(get_db), user: User = Depends(require_provider_or_admin)):
    meal = meal_service.get_meal_or_404(db, meal_id)
    meal_service.ensure_can_modify(meal, user)
    meal_service.delete_meal(db, meal, user)