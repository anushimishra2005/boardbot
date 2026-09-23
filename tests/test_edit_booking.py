from datetime import datetime, timezone

from api.agent.tools import EditBookingInput, edit_booking
from api.core.database import SessionLocal


def main():
    db = SessionLocal()

    try:
        data = EditBookingInput(
            booking_id=105,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2035,
                9,
                24,
                15,
                0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2035,
                9,
                24,
                16,
                0,
                tzinfo=timezone.utc,
            ),
            attendees=6,
        )

        result = edit_booking(
            db=db,
            data=data,
        )

        print("\nEDIT BOOKING RESULT:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()