from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.db.session import get_db
from app.dependencies.roles import require_admin
from app.models.category import Category
from app.models.meal import Meal
from app.schemas.category import CategoryIn, CategoryOut

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])
logger = get_logger("categories")

ADMIN_ERRORS = {401: {"description": "Not logged in"}, 403: {"description": "ADMIN only"}}


def _get_or_404(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found")
    return category


def _ensure_name_free(db: Session, name: str, ignore_id: int | None = None) -> None:
    stmt = select(Category.id).where(func.lower(Category.name) == name.lower())
    existing_id = db.scalar(stmt)
    if existing_id is not None and existing_id != ignore_id:
        raise HTTPException(status.HTTP_409_CONFLICT, "A category with this name already exists")


@router.get("", response_model=list[CategoryOut], summary="List categories (public)")
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.name)).all()


@router.post(
    "", response_model=CategoryOut, status_code=status.HTTP_201_CREATED, summary="Create a category (ADMIN)",
    responses={**ADMIN_ERRORS, 409: {"description": "Name already exists"}},
)
def create_category(payload: CategoryIn, db: Session = Depends(get_db), admin=Depends(require_admin)):
    _ensure_name_free(db, payload.name)
    category = Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    logger.info("Category created: id=%s by admin_id=%s", category.id, admin.id)
    return category


@router.put(
    "/{category_id}", response_model=CategoryOut, summary="Update a category (ADMIN)",
    responses={**ADMIN_ERRORS, 404: {"description": "Not found"}, 409: {"description": "Name already exists"}},
)
def update_category(category_id: int, payload: CategoryIn, db: Session = Depends(get_db), admin=Depends(require_admin)):
    category = _get_or_404(db, category_id)
    _ensure_name_free(db, payload.name, ignore_id=category_id)
    category.name = payload.name
    category.description = payload.description
    db.commit()
    db.refresh(category)
    logger.info("Category updated: id=%s by admin_id=%s", category.id, admin.id)
    return category


@router.delete(
    "/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a category (ADMIN)",
    responses={**ADMIN_ERRORS, 404: {"description": "Not found"}, 409: {"description": "Category is in use"}},
)
def delete_category(category_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    category = _get_or_404(db, category_id)
    in_use = db.scalar(select(func.count()).select_from(Meal).where(Meal.category_id == category_id))
    if in_use:
        raise HTTPException(status.HTTP_409_CONFLICT, "This category is used by meals and cannot be deleted")
    db.delete(category)
    db.commit()
    logger.info("Category deleted: id=%s by admin_id=%s", category_id, admin.id)