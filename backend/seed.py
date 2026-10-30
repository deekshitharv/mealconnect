"""Fills the database with DEMO data. Safe to run more than once.
The passwords below are for local demos only. Never use them in real life."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Category, Location, Meal, User

DEMO_USERS = [
    ("Admin", "admin@example.com", "Admin@12345", "ADMIN"),
    ("Green Leaf Cafe", "provider@example.com", "Provider@123", "PROVIDER"),
    ("Sunrise Bakers", "provider2@example.com", "Provider@123", "PROVIDER"),
    ("Asha Rao", "user@example.com", "User@12345", "USER"),
    ("Ravi Kumar", "user2@example.com", "User@12345", "USER"),
]

CATEGORIES = [
    ("Breakfast", "Morning meals"), ("Lunch", "Midday meals"), ("Dinner", "Evening meals"),
    ("Snacks", "Light bites"), ("Bakery", "Breads and pastries"), ("Beverages", "Drinks"),
    ("Other", "Anything else"),
]

LOCATIONS = [
    ("Green Leaf Cafe", "12 MG Road", "Bangalore"),
    ("Sunrise Bakery", "45 Church Street", "Bangalore"),
    ("Community Kitchen Mysuru", "8 Temple Road", "Mysuru"),
    ("Event Hall Chennai", "22 Anna Salai", "Chennai"),
]

# name, description, quantity, category, location, provider email, starts (hours from now), ends (hours from now)
MEALS = [
    ("Veg fried rice", "Freshly cooked veg fried rice, packed in individual boxes.", 10, "Lunch", "Green Leaf Cafe", "provider@example.com", -1, 6),
    ("Paneer wrap", "Paneer tikka wraps left over from the lunch rush.", 6, "Lunch", "Green Leaf Cafe", "provider@example.com", -1, 1),
    ("Masala dosa", "Crisp dosas with potato filling and chutney.", 8, "Breakfast", "Community Kitchen Mysuru", "provider@example.com", -2, 4),
    ("Veg dinner thali", "Rice, dal, two curries and chapati.", 7, "Dinner", "Event Hall Chennai", "provider@example.com", 2, 9),
    ("Idli and sambar", "Soft idlis with sambar. All portions are taken.", 0, "Breakfast", "Community Kitchen Mysuru", "provider@example.com", -3, 5),
    ("Lemon rice", "Lemon rice from yesterday's event. Pickup window is over.", 5, "Lunch", "Green Leaf Cafe", "provider@example.com", -10, -2),
    ("Assorted bread loaves", "Fresh bread loaves baked this morning.", 12, "Bakery", "Sunrise Bakery", "provider2@example.com", -1, 8),
    ("Chocolate muffins", "Chocolate chip muffins, baked today.", 4, "Bakery", "Sunrise Bakery", "provider2@example.com", -1, 3),
    ("Evening snack box", "Samosas and sandwiches, available this evening.", 15, "Snacks", "Sunrise Bakery", "provider2@example.com", 1, 10),
    ("Mango lassi", "Chilled mango lassi in sealed cups.", 10, "Beverages", "Green Leaf Cafe", "provider2@example.com", -1, 5),
]


def seed() -> None:
    with SessionLocal() as db:
        users = {}
        for name, email, password, role in DEMO_USERS:
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(name=name, email=email, password_hash=hash_password(password), role=role)
                db.add(user)
            users[email] = user

        categories = {}
        for name, description in CATEGORIES:
            category = db.scalar(select(Category).where(Category.name == name))
            if category is None:
                category = Category(name=name, description=description)
                db.add(category)
            categories[name] = category

        locations = {}
        for name, address, city in LOCATIONS:
            location = db.scalar(select(Location).where(Location.name == name))
            if location is None:
                location = Location(name=name, address=address, city=city)
                db.add(location)
            locations[name] = location

        db.flush()  # gives the new rows their ids

        if db.scalar(select(Meal.id).limit(1)) is None:
            now = datetime.now(timezone.utc)
            for name, description, qty, cat, loc, provider, start_h, end_h in MEALS:
                db.add(
                    Meal(
                        provider_id=users[provider].id,
                        category_id=categories[cat].id,
                        location_id=locations[loc].id,
                        name=name,
                        description=description,
                        quantity=qty,
                        available_from=now + timedelta(hours=start_h),
                        available_until=now + timedelta(hours=end_h),
                        status="FULLY_RESERVED" if qty == 0 else "AVAILABLE",
                    )
                )
            print(f"Added {len(MEALS)} meals")
        else:
            print("Meals already exist, skipping meals")

        db.commit()
    print("Seed complete")


if __name__ == "__main__":
    seed()