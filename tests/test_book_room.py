from datetime import datetime, timezone

from api.agent.tools import BookRoomInput, book_room
from api.core.database import SessionLocal


def main():
    db = SessionLocal()

    try:
        data = BookRoomInput(
            user_id=1,
            room_id=1,
            start_time=datetime(
                2035, 9, 24, 15, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2035, 9, 24, 16, 0,
                tzinfo=timezone.utc,
            ),
            attendees=5,
        )

        result = book_room(
            db=db,
            data=data,
        )

        print("\nBOOK ROOM RESULT:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()