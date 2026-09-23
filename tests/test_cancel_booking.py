from api.agent.tools import CancelBookingInput, cancel_booking_tool
from api.core.database import SessionLocal


def main():
    db = SessionLocal()

    try:
        data = CancelBookingInput(
            booking_id=105,
            user_id=1,
        )

        result = cancel_booking_tool(
            db=db,
            data=data,
        )

        print("\nCANCEL BOOKING RESULT:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()