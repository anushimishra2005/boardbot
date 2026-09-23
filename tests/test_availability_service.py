from datetime import datetime, timezone

from api.core.database import SessionLocal
from api.services.availability_service import check_room_availability
from api.services.booking_service import create_booking


def test_room_is_available_when_no_booking_exists():
    db = SessionLocal()

    try:
        available = check_room_availability(
            db=db,
            room_id=1,
            start_time=datetime(
                2031, 2, 1, 10, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2031, 2, 1, 11, 0,
                tzinfo=timezone.utc,
            ),
        )

        assert available is True

    finally:
        db.close()


def test_room_is_unavailable_when_booking_overlaps():
    db = SessionLocal()
    booking = None

    try:
        booking = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2031, 2, 2, 10, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2031, 2, 2, 11, 0,
                tzinfo=timezone.utc,
            ),
            attendees=5,
        )

        available = check_room_availability(
            db=db,
            room_id=1,
            start_time=datetime(
                2031, 2, 2, 10, 30,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2031, 2, 2, 11, 30,
                tzinfo=timezone.utc,
            ),
        )

        assert available is False

    finally:
        if booking is not None:
            db.delete(booking)
            db.commit()
        else:
            db.rollback()

        db.close()