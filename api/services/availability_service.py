from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.booking import Booking


def check_room_availability(
    db: Session,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
) -> bool:
    """Return True when a room has no overlapping booking."""

    existing_booking = db.execute(
        select(Booking).where(
            Booking.room_id == room_id,
            Booking.start_time < end_time,
            Booking.end_time > start_time,
        )
    ).scalar_one_or_none()

    return existing_booking is None