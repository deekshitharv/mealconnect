# Importing every model here makes sure SQLAlchemy "knows" all tables.
# Alembic (Phase 5) relies on this.
from app.models.category import Category
from app.models.location import Location
from app.models.meal import Meal
from app.models.reservation import Reservation
from app.models.user import User

__all__ = ["User", "Category", "Location", "Meal", "Reservation"]