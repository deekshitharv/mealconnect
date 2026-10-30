"""Resets the demo meals: fresh pickup times, original quantities, and removes
reservations on them. Run it whenever the demo meals have expired.
Only touches the meals created by seed.py (matched by name)."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models import Meal, Reservation
from seed import MEALS


def refresh() -> None:
    now = datetime.now(timezone.utc)
    refreshed = 0
    with SessionLocal() as db:
        for name, _desc, qty, _cat, _loc, _provider, start_h, end_h in MEALS:
            meal = db.scalar(select(Meal).where(Meal.name == name))
            if meal is None:
                continue
            db.execute(delete(Reservation).where(Reservation.meal_id == meal.id))
            meal.quantity = qty
            meal.available_from = now + timedelta(hours=start_h)
            meal.available_until = now + timedelta(hours=end_h)
            meal.status = "FULLY_RESERVED" if qty == 0 else "AVAILABLE"
            refreshed += 1
        db.commit()
    print(f"Refreshed {refreshed} demo meals")


if __name__ == "__main__":
    refresh()
    