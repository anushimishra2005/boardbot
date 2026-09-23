from api.core.database import SessionLocal
from api.services.room_service import (
    get_room,
    list_rooms,
)


def test_get_room():
    db = SessionLocal()

    try:
        room = get_room(
            db=db,
            room_id=1,
        )

        assert room is not None
        assert room.id == 1
        assert room.name == "Atlas"

    finally:
        db.close()


def test_list_rooms():
    db = SessionLocal()

    try:
        rooms = list_rooms(db)

        assert len(rooms) >= 3

        room_names = [room.name for room in rooms]

        assert "Atlas" in room_names
        assert "Orion" in room_names
        assert "Nova" in room_names

    finally:
        db.close()