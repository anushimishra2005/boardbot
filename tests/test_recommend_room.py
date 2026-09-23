from api.agent.tools import RecommendRoomInput, recommend_room
from api.core.database import SessionLocal


def main():
    db = SessionLocal()

    try:
        data = RecommendRoomInput(
            attendees=5,
            required_equipment=["whiteboard"],
        )

        result = recommend_room(
            db=db,
            data=data,
        )

        print("\nRECOMMEND ROOM RESULT:")
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()