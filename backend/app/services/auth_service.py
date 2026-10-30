from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.logging_config import get_logger
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import UserRegister

logger = get_logger("auth")


def register_user(db: Session, payload: UserRegister) -> User:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Two people registering the same email at the same moment: the database's
        # UNIQUE rule catches it even if our check above did not.
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

    db.refresh(user)
    logger.info("User registered: id=%s role=%s", user.id, user.role)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(password, user.password_hash):
        logger.warning("Failed login attempt for email=%s", email)
        # Same message for "no such email" and "wrong password", so attackers learn nothing.
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("User logged in: id=%s", user.id)
    return user