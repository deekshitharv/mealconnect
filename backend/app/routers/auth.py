from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import TokenOut, UserLogin, UserOut, UserRegister
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
    responses={409: {"description": "Email already registered"}},
)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Create a USER or PROVIDER account. The password is hashed before saving."""
    return auth_service.register_user(db, payload)


@router.post(
    "/login",
    response_model=TokenOut,
    summary="Log in and get a JWT token",
    responses={401: {"description": "Incorrect email or password"}},
)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """Check email and password. On success, returns a token to send with later requests."""
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    token = create_access_token(user.id, user.role)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get the logged-in user",
    responses={401: {"description": "Missing, invalid or expired token"}},
)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Requires a valid token."""
    return current_user