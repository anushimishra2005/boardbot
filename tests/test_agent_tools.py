from datetime import datetime, timezone

from api.agent.tools import (
    BatchMoveBookingsInput,
    CheckAvailabilityInput,
    batch_move_bookings_tool,
)
from api.agent.tool_schemas import CHECK_AVAILABILITY_TOOL

def test_check_availability_input_accepts_valid_data():
    data = CheckAvailabilityInput(
        room_id=1,
        start_time=datetime(
            2026, 9, 24, 15, 0, tzinfo=timezone.utc
        ),
        end_time=datetime(
            2026, 9, 24, 16, 0, tzinfo=timezone.utc
        ),
    )

    assert data.room_id == 1
    assert data.start_time < data.end_time
def test_check_availability_tool_schema():
    assert CHECK_AVAILABILITY_TOOL["type"] == "function"
    assert CHECK_AVAILABILITY_TOOL["name"] == "check_availability"

    parameters = CHECK_AVAILABILITY_TOOL["parameters"]

    assert parameters["required"] == [
        "room_id",
        "start_time",
        "end_time",
    ]

    assert parameters["additionalProperties"] is False
def test_batch_move_bookings_tool():
    from api.core.database import SessionLocal
    from api.services.booking_service import create_booking

    db = SessionLocal()
    booking_one = None
    booking_two = None

    try:
        booking_one = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2033, 1, 10, 10, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2033, 1, 10, 11, 0,
                tzinfo=timezone.utc,
            ),
            attendees=4,
        )

        booking_two = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2033, 1, 10, 12, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2033, 1, 10, 13, 0,
                tzinfo=timezone.utc,
            ),
            attendees=5,
        )

        data = BatchMoveBookingsInput(
            user_id=1,
            moves=[
                {
                    "booking_id": booking_one.id,
                    "room_id": 1,
                    "start_time": datetime(
                        2033, 1, 11, 10, 0,
                        tzinfo=timezone.utc,
                    ),
                    "end_time": datetime(
                        2033, 1, 11, 11, 0,
                        tzinfo=timezone.utc,
                    ),
                    "attendees": 4,
                },
                {
                    "booking_id": booking_two.id,
                    "room_id": 1,
                    "start_time": datetime(
                        2033, 1, 11, 12, 0,
                        tzinfo=timezone.utc,
                    ),
                    "end_time": datetime(
                        2033, 1, 11, 13, 0,
                        tzinfo=timezone.utc,
                    ),
                    "attendees": 5,
                },
            ],
        )

        result = batch_move_bookings_tool(
            db=db,
            data=data,
        )

        assert result["success"] is True
        assert result["user_id"] == 1
        assert result["moved_count"] == 2
        assert len(result["bookings"]) == 2

        assert result["bookings"][0]["booking_id"] == booking_one.id
        assert result["bookings"][1]["booking_id"] == booking_two.id

    finally:
        if booking_one is not None:
            existing = db.get(
                type(booking_one),
                booking_one.id,
            )
            if existing is not None:
                db.delete(existing)

        if booking_two is not None:
            existing = db.get(
                type(booking_two),
                booking_two.id,
            )
            if existing is not None:
                db.delete(existing)

        db.commit()
        db.close()