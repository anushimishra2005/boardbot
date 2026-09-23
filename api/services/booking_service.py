from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.booking import Booking
from api.models.room import Room
from api.services.scheduling_engine import (
    validate_business_hours,
    validate_capacity,
    validate_not_in_past,
    validate_time_range,
)


def get_booking(
    db: Session,
    booking_id: int,
    user_id: int | None = None,
):
    query = select(Booking).where(
        Booking.id == booking_id
    )

    if user_id is not None:
        query = query.where(
            Booking.user_id == user_id
        )

    return db.execute(query).scalar_one_or_none()


def create_booking(
    db: Session,
    user_id: int,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    attendees: int,
) -> Booking:
    """Validate and persist a booking."""

    valid, error = validate_time_range(
        start_time,
        end_time,
    )

    if not valid:
        raise ValueError(error)

    valid, error = validate_business_hours(
        start_time,
        end_time,
    )

    if not valid:
        raise ValueError(error)

    valid, error = validate_not_in_past(
        start_time,
    )

    if not valid:
        raise ValueError(error)

    room = db.get(Room, room_id)

    if room is None:
        raise ValueError(
            f"Room with ID {room_id} does not exist."
        )

    valid, error = validate_capacity(
        attendees,
        room.capacity,
    )

    if not valid:
        raise ValueError(error)

    existing_booking = db.execute(
        select(Booking).where(
            Booking.room_id == room_id,
            Booking.start_time < end_time,
            Booking.end_time > start_time,
        )
    ).scalar_one_or_none()

    if existing_booking is not None:
        raise ValueError(
            "The requested time overlaps with an existing booking."
        )

    booking = Booking(
        user_id=user_id,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
        attendees=attendees,
        status="confirmed",
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking

def list_bookings(db: Session, user_id: int | None = None):
    query = select(Booking)

    if user_id is not None:
        query = query.where(Booking.user_id == user_id)

    return db.scalars(
        query.order_by(Booking.start_time)
    ).all()
def update_booking(
    db: Session,
    booking_id: int,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    attendees: int,
    user_id: int | None = None,
) -> Booking:
    """Validate and update an existing booking."""

    query = select(Booking).where(
        Booking.id == booking_id
    )

    if user_id is not None:
        query = query.where(
            Booking.user_id == user_id
        )

    booking = db.execute(query).scalar_one_or_none()

    if booking is None:
        raise ValueError(
            f"Booking with ID {booking_id} does not exist."
        )

    valid, error = validate_time_range(
        start_time,
        end_time,
    )

    if not valid:
        raise ValueError(error)

    valid, error = validate_business_hours(
        start_time,
        end_time,
    )

    if not valid:
        raise ValueError(error)

    valid, error = validate_not_in_past(
        start_time,
    )

    if not valid:
        raise ValueError(error)

    room = db.get(Room, room_id)

    if room is None:
        raise ValueError(
            f"Room with ID {room_id} does not exist."
        )

    valid, error = validate_capacity(
        attendees,
        room.capacity,
    )

    if not valid:
        raise ValueError(error)

    existing_booking = db.execute(
        select(Booking).where(
            Booking.id != booking_id,
            Booking.room_id == room_id,
            Booking.start_time < end_time,
            Booking.end_time > start_time,
        )
    ).scalar_one_or_none()

    if existing_booking is not None:
        raise ValueError(
            "The requested time overlaps with an existing booking."
        )

    booking.room_id = room_id
    booking.start_time = start_time
    booking.end_time = end_time
    booking.attendees = attendees

    db.commit()
    db.refresh(booking)

    return booking

def cancel_booking(
    db: Session,
    booking_id: int,
    user_id: int | None = None,
) -> Booking:
    """Cancel an existing booking."""

    query = select(Booking).where(
        Booking.id == booking_id
    )

    if user_id is not None:
        query = query.where(
            Booking.user_id == user_id
        )

    booking = db.execute(query).scalar_one_or_none()

    if booking is None:
        raise ValueError(
            f"Booking with ID {booking_id} does not exist."
        )

    booking.status = "cancelled"

    db.commit()
    db.refresh(booking)

    return booking

def batch_move_bookings(
    db: Session,
    moves: list[dict],
    user_id: int | None = None,
) -> list[Booking]:
    """Validate and move multiple bookings atomically."""

    bookings = []

    try:
        # Phase 1: Load and validate every booking
        for move in moves:
            booking_id = move["booking_id"]

            query = select(Booking).where(
                Booking.id == booking_id
            )

            if user_id is not None:
                query = query.where(
                    Booking.user_id == user_id
                )

            booking = db.execute(
                query
            ).scalar_one_or_none()

            if booking is None:
                raise ValueError(
                    f"Booking with ID {booking_id} does not exist."
                )

            # Validate proposed time range
            valid, error = validate_time_range(
                move["start_time"],
                move["end_time"],
            )

            if not valid:
                raise ValueError(error)

            # Validate business hours
            valid, error = validate_business_hours(
                move["start_time"],
                move["end_time"],
            )

            if not valid:
                raise ValueError(error)

            # Validate future booking
            valid, error = validate_not_in_past(
                move["start_time"],
            )

            if not valid:
                raise ValueError(error)

            # Validate room
            room = db.get(
                Room,
                move["room_id"],
            )

            if room is None:
                raise ValueError(
                    f"Room with ID {move['room_id']} does not exist."
                )

            # Validate capacity
            valid, error = validate_capacity(
                move["attendees"],
                room.capacity,
            )

            if not valid:
                raise ValueError(error)

            # Check conflicts with OTHER existing bookings
            existing_booking = db.execute(
                select(Booking).where(
                    Booking.id != booking_id,
                    Booking.room_id == move["room_id"],
                    Booking.status != "cancelled",
                    Booking.start_time < move["end_time"],
                    Booking.end_time > move["start_time"],
                )
            ).scalar_one_or_none()

            if existing_booking is not None:
                raise ValueError(
                    "One of the requested moves overlaps "
                    "with an existing booking."
                )

            bookings.append(
                (
                    booking,
                    move,
                )
            )

        # Phase 2: Apply every move
        updated_bookings = []

        for booking, move in bookings:
            booking.room_id = move["room_id"]
            booking.start_time = move["start_time"]
            booking.end_time = move["end_time"]
            booking.attendees = move["attendees"]

            updated_bookings.append(booking)

        # Phase 3: Commit everything together
        db.commit()

        for booking in updated_bookings:
            db.refresh(booking)

        return updated_bookings

    except Exception:
        db.rollback()
        raise