from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.user import User
from api.core.security import (
    create_access_token,
    verify_password,
)


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> str | None:
    """Validate credentials and return a JWT token."""

    user = db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return create_access_token(user.id)