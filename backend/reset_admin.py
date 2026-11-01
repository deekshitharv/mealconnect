"""Resets the admin password in the database named by DATABASE_URL."""
import os
from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import User

password = os.environ["SEED_ADMIN_PASSWORD"]

with SessionLocal() as db:
    admin = db.scalar(select(User).where(User.email == "admin@example.com"))
    if admin is None:
        print("Admin user not found")
    else:
        admin.password_hash = hash_password(password)
        db.commit()
        print("Admin password updated")