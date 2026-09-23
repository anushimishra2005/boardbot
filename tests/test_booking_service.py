from api.services.booking_service import (
    batch_move_bookings,
    cancel_booking,
    create_booking,
    get_booking,
    list_bookings,
    update_booking,
)
from datetime import datetime, timezone
import pytest
from api.core.database import SessionLocal

def test_get_booking_function_exists():
    assert callable(get_booking)

def test_create_booking_function_exists():
    assert callable(create_booking)
def test_create_and_get_booking():
    db = SessionLocal()
    booking = None

    try:
        booking = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(2031, 1, 1, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2031, 1, 1, 11, 0, tzinfo=timezone.utc),
            attendees=5,
        )

        fetched_booking = get_booking(
            db=db,
            booking_id=booking.id,
        )

        assert fetched_booking is not None
        assert fetched_booking.id == booking.id
        assert fetched_booking.room_id == 1
        assert fetched_booking.attendees == 5

    finally:
        if booking is not None:
            db.delete(booking)
            db.commit()
        else:
            db.rollback()

        db.close()
def test_create_booking_rejects_over_capacity():
    db = SessionLocal()

    try:
        with pytest.raises(
            ValueError,
            match="Room capacity is 10, but 15 attendees were requested.",
        ):
            create_booking(
                db=db,
                user_id=1,
                room_id=1,
                start_time=datetime(
                    2031, 1, 2, 10, 0,
                    tzinfo=timezone.utc,
                ),
                end_time=datetime(
                    2031, 1, 2, 11, 0,
                    tzinfo=timezone.utc,
                ),
                attendees=15,
            )

    finally:
        db.rollback()
        db.close()


def test_create_booking_rejects_outside_business_hours():
    db = SessionLocal()

    try:
        with pytest.raises(
            ValueError,
            match="Bookings must be between 09:00 and 21:00.",
        ):
            create_booking(
                db=db,
                user_id=1,
                room_id=1,
                start_time=datetime(
                    2031, 1, 3, 8, 0,
                    tzinfo=timezone.utc,
                ),
                end_time=datetime(
                    2031, 1, 3, 10, 0,
                    tzinfo=timezone.utc,
                ),
                attendees=5,
            )

    finally:
        db.rollback()
        db.close()
def test_create_booking_rejects_overlap():
    db = SessionLocal()
    booking = None

    try:
        booking = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2031, 1, 5, 10, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2031, 1, 5, 11, 0,
                tzinfo=timezone.utc,
            ),
            attendees=5,
        )

        with pytest.raises(
            ValueError,
            match="The requested time overlaps with an existing booking.",
        ):
            create_booking(
                db=db,
                user_id=1,
                room_id=1,
                start_time=datetime(
                    2031, 1, 5, 10, 30,
                    tzinfo=timezone.utc,
                ),
                end_time=datetime(
                    2031, 1, 5, 11, 30,
                    tzinfo=timezone.utc,
                ),
                attendees=5,
            )

    finally:
        if booking is not None:
            db.delete(booking)
            db.commit()
        else:
            db.rollback()

        db.close()
def test_list_bookings():
    db = SessionLocal()

    try:
        bookings = list_bookings(db)

        assert isinstance(bookings, list)
        assert len(bookings) >= 1

        for booking in bookings:
            assert booking.id is not None
            assert booking.room_id is not None
            assert booking.user_id is not None

    finally:
        db.close()

def test_cancel_booking():
    db = SessionLocal()
    booking = None

    try:
        booking = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2031, 4, 1, 10, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2031, 4, 1, 11, 0,
                tzinfo=timezone.utc,
            ),
            attendees=5,
        )

        cancelled_booking = cancel_booking(
            db=db,
            booking_id=booking.id,
        )

        assert cancelled_booking.id == booking.id
        assert cancelled_booking.status == "cancelled"

    finally:
        if booking is not None:
            db.delete(booking)
            db.commit()
        else:
            db.rollback()

        db.close()
def test_batch_move_bookings():
    db = SessionLocal()
    booking_one = None
    booking_two = None

    try:
        booking_one = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2032, 1, 10, 10, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2032, 1, 10, 11, 0,
                tzinfo=timezone.utc,
            ),
            attendees=4,
        )

        booking_two = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2032, 1, 10, 12, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2032, 1, 10, 13, 0,
                tzinfo=timezone.utc,
            ),
            attendees=5,
        )

        moved_bookings = batch_move_bookings(
            db=db,
            user_id=1,
            moves=[
                {
                    "booking_id": booking_one.id,
                    "room_id": 1,
                    "start_time": datetime(
                        2032, 1, 11, 10, 0,
                        tzinfo=timezone.utc,
                    ),
                    "end_time": datetime(
                        2032, 1, 11, 11, 0,
                        tzinfo=timezone.utc,
                    ),
                    "attendees": 4,
                },
                {
                    "booking_id": booking_two.id,
                    "room_id": 1,
                    "start_time": datetime(
                        2032, 1, 11, 12, 0,
                        tzinfo=timezone.utc,
                    ),
                    "end_time": datetime(
                        2032, 1, 11, 13, 0,
                        tzinfo=timezone.utc,
                    ),
                    "attendees": 5,
                },
            ],
        )

        assert len(moved_bookings) == 2

        assert moved_bookings[0].start_time.date().isoformat() == "2032-01-11"
        assert moved_bookings[1].start_time.date().isoformat() == "2032-01-11"

        assert moved_bookings[0].room_id == 1
        assert moved_bookings[1].room_id == 1

    finally:
        if booking_one is not None:
            db.delete(
                db.get(type(booking_one), booking_one.id)
            )

        if booking_two is not None:
            db.delete(
                db.get(type(booking_two), booking_two.id)
            )

        db.commit()
        db.close()


def test_batch_move_bookings_rolls_back_on_failure():
    db = SessionLocal()
    booking_one = None
    booking_two = None

    try:
        booking_one = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2032, 2, 10, 10, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2032, 2, 10, 11, 0,
                tzinfo=timezone.utc,
            ),
            attendees=4,
        )

        booking_two = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2032, 2, 10, 12, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2032, 2, 10, 13, 0,
                tzinfo=timezone.utc,
            ),
            attendees=5,
        )

        original_start_one = booking_one.start_time
        original_start_two = booking_two.start_time

        with pytest.raises(
            ValueError,
            match="Room with ID 999 does not exist.",
        ):
            batch_move_bookings(
                db=db,
                user_id=1,
                moves=[
                    {
                        "booking_id": booking_one.id,
                        "room_id": 1,
                        "start_time": datetime(
                            2032, 2, 11, 10, 0,
                            tzinfo=timezone.utc,
                        ),
                        "end_time": datetime(
                            2032, 2, 11, 11, 0,
                            tzinfo=timezone.utc,
                        ),
                        "attendees": 4,
                    },
                    {
                        "booking_id": booking_two.id,
                        "room_id": 999,
                        "start_time": datetime(
                            2032, 2, 11, 12, 0,
                            tzinfo=timezone.utc,
                        ),
                        "end_time": datetime(
                            2032, 2, 11, 13, 0,
                            tzinfo=timezone.utc,
                        ),
                        "attendees": 5,
                    },
                ],
            )

        db.refresh(booking_one)
        db.refresh(booking_two)

        assert booking_one.start_time == original_start_one
        assert booking_two.start_time == original_start_two

    finally:
        if booking_one is not None:
            existing = db.get(type(booking_one), booking_one.id)
            if existing is not None:
                db.delete(existing)

        if booking_two is not None:
            existing = db.get(type(booking_two), booking_two.id)
            if existing is not None:
                db.delete(existing)

        db.commit()
        db.close()