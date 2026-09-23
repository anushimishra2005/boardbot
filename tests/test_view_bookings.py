from api.agent.tools import ViewBookingsInput, view_bookings
from api.core.database import SessionLocal


def main():
    db = SessionLocal()

    try:
        data = ViewBookingsInput(
            user_id=1,
        )

        result = view_bookings(
            db=db,
            data=data,
        )

        print("\nVIEW BOOKINGS RESULT:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()