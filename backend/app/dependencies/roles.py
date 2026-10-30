from fastapi import Depends, HTTPException, status

from app.dependencies.auth import get_current_user
from app.models.user import User


def require_roles(*allowed_roles: str):
    """Build a dependency that only lets users with one of these roles through."""

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "You do not have permission to perform this action"
            )
        return current_user

    return checker


require_provider = require_roles("PROVIDER")
require_admin = require_roles("ADMIN")
require_provider_or_admin = require_roles("PROVIDER", "ADMIN")