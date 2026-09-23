from sqlalchemy import select

from api.core.database import SessionLocal
from api.core.security import hash_password
from api.models.user import User


def main():
    db = SessionLocal()

    try:
        users = db.scalars(
            select(User).where(
                User.email.in_(
                    [
                        "anushi@example.com",
                        "demo@example.com",
                    ]
                )
            )
        ).all()

        for user in users:
            user.password_hash = hash_password(
                "demo-password"
            )

        db.commit()

        print(
            f"Updated {len(users)} demo user password(s)."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()