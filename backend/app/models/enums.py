import enum


class UserRole(str, enum.Enum):
    USER = "USER"
    PROVIDER = "PROVIDER"
    ADMIN = "ADMIN"


class MealStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    FULLY_RESERVED = "FULLY_RESERVED"
    EXPIRED = "EXPIRED"
    UNAVAILABLE = "UNAVAILABLE"


class ReservationStatus(str, enum.Enum):
    RESERVED = "RESERVED"
    COLLECTED = "COLLECTED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


def sql_values(enum_class) -> str:
    """Turn an enum into SQL text like: 'USER', 'PROVIDER', 'ADMIN' (for CHECK constraints)."""
    return ", ".join(f"'{item.value}'" for item in enum_class) 