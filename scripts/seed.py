from api.core.database import SessionLocal
from api.models import (
    Equipment,
    Room,
    RoomEquipment,
    User,
)
from api.core.security import hash_password


def seed_database():
    db = SessionLocal()

    try:
        # Users
        user1 = User(
            name="Anushi Mishra",
            email="anushi@example.com",
            department="Engineering",
            password_hash=hash_password("demo-password"),
        )

        user2 = User(
            name="Demo User",
            email="demo@example.com",
            department="Engineering",
            password_hash=hash_password("demo-password"),
        )

        db.add_all([user1, user2])

        # Rooms
        room1 = Room(
            name="Atlas",
            capacity=10,
            location="1st Floor",
        )

        room2 = Room(
            name="Orion",
            capacity=20,
            location="2nd Floor",
        )

        room3 = Room(
            name="Nova",
            capacity=6,
            location="1st Floor",
        )

        db.add_all([room1, room2, room3])

        # Equipment
        projector = Equipment(name="projector")
        whiteboard = Equipment(name="whiteboard")
        video_conferencing = Equipment(
            name="video conferencing"
        )
        speaker = Equipment(name="speaker")

        db.add_all([
            projector,
            whiteboard,
            video_conferencing,
            speaker,
        ])

        db.commit()

        # Room equipment
        db.add_all([
            RoomEquipment(
                room_id=room1.id,
                equipment_id=projector.id,
            ),
            RoomEquipment(
                room_id=room1.id,
                equipment_id=whiteboard.id,
            ),
            RoomEquipment(
                room_id=room2.id,
                equipment_id=projector.id,
            ),
            RoomEquipment(
                room_id=room2.id,
                equipment_id=whiteboard.id,
            ),
            RoomEquipment(
                room_id=room2.id,
                equipment_id=video_conferencing.id,
            ),
            RoomEquipment(
                room_id=room2.id,
                equipment_id=speaker.id,
            ),
            RoomEquipment(
                room_id=room3.id,
                equipment_id=whiteboard.id,
            ),
        ])

        db.commit()

        print("Database seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()