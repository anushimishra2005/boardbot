from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.room import Room


def get_room(
    db: Session,
    room_id: int,
) -> Room | None:
    """Fetch a room by ID."""

    return db.get(Room, room_id)


def list_rooms(
    db: Session,
) -> list[Room]:
    """Return all rooms ordered by name."""

    return list(
        db.scalars(
            select(Room).order_by(Room.name)
        ).all()
    )