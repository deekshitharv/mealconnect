from datetime import datetime, timedelta, timezone

from app.core.security import hash_password
from app.models import Meal, User

PASSWORD = "StrongPass123"


def hours(n: float) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=n)


def make_user(db, email: str, role: str = "USER", name: str = "Test User") -> User:
    user = User(name=name, email=email, password_hash=hash_password(PASSWORD), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_headers(client, email: str) -> dict:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def make_meal(db, provider_id, category_id, location_id, *, quantity=10, start_h=-1, end_h=6, name="Test meal") -> Meal:
    """Insert a meal directly (lets us create already-expired meals, which the API refuses)."""
    meal = Meal(
        provider_id=provider_id,
        category_id=category_id,
        location_id=location_id,
        name=name,
        description="Test",
        quantity=quantity,
        available_from=hours(start_h),
        available_until=hours(end_h),
        status="FULLY_RESERVED" if quantity == 0 else "AVAILABLE",
    )
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal


def meal_payload(category_id: int, location_id: int, **overrides) -> dict:
    data = {
        "name": "Veg fried rice",
        "description": "Freshly cooked",
        "quantity": 10,
        "category_id": category_id,
        "location_id": location_id,
        "available_from": hours(-1).isoformat(),
        "available_until": hours(6).isoformat(),
        "image_url": "",
    }
    data.update(overrides)
    return data