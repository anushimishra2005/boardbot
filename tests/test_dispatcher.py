from datetime import datetime, timezone

from api.agent.dispatcher import dispatch_tool
from api.agent.tools import RecommendRoomInput, recommend_room
from api.core.database import SessionLocal
from api.services.booking_service import create_booking

def test_dispatch_check_availability():
    db = SessionLocal()

    try:
        result = dispatch_tool(
            tool_name="check_availability",
            arguments={
                "room_id": 1,
                "start_time": "2026-09-24T15:00:00Z",
                "end_time": "2026-09-24T16:00:00Z",
            },
            db=db,
        )

        assert result["room_id"] == 1
        assert result["available"] in [True, False]

    finally:
        db.close()


def test_dispatch_invalid_room_id():
    db = SessionLocal()

    try:
        result = dispatch_tool(
            tool_name="check_availability",
            arguments={
                "room_id": -1,
                "start_time": "2026-09-24T15:00:00Z",
                "end_time": "2026-09-24T16:00:00Z",
            },
            db=db,
        )

        assert result["success"] is False
        assert result["error_type"] == "validation_error"

    finally:
        db.close()


def test_recommend_room():
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

        assert result["success"] is True
        assert result["requested_attendees"] == 5
        assert result["required_equipment"] == ["whiteboard"]

        recommendations = result["recommendations"]

        assert len(recommendations) > 0
        assert recommendations[0]["name"] == "Nova"
        assert recommendations[0]["capacity"] >= 5
        assert "whiteboard" in recommendations[0]["equipment"]

    finally:
        db.close()


def test_dispatch_recommend_room():
    db = SessionLocal()

    try:
        result = dispatch_tool(
            tool_name="recommend_room",
            arguments={
                "attendees": 5,
                "required_equipment": ["whiteboard"],
            },
            db=db,
        )

        assert result["success"] is True
        assert result["requested_attendees"] == 5
        assert result["recommendations"]

        assert result["recommendations"][0]["name"] == "Nova"

    finally:
        db.close()
def test_dispatch_view_bookings():
    db = SessionLocal()

    try:
        result = dispatch_tool(
            tool_name="view_bookings",
            arguments={
                "user_id": 1,
            },
            db=db,
        )

        assert result["success"] is True
        assert result["user_id"] == 1
        assert isinstance(result["bookings"], list)

        if result["bookings"]:
            booking = result["bookings"][0]

            assert "booking_id" in booking
            assert "room_id" in booking
            assert "start_time" in booking
            assert "end_time" in booking
            assert "attendees" in booking
            assert "status" in booking

    finally:
        db.close()

def test_dispatch_edit_booking():
    db = SessionLocal()
    booking = None

    try:
        booking = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2031, 3, 9, 18, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2031, 3, 9, 19, 0,
                tzinfo=timezone.utc,
            ),
            attendees=6,
        )

        result = dispatch_tool(
            tool_name="edit_booking",
            arguments={
                "booking_id": booking.id,
                "user_id": 1,
                "room_id": 1,
                "start_time": "2031-03-10T18:00:00Z",
                "end_time": "2031-03-10T19:00:00Z",
                "attendees": 6,
            },
            db=db,
        )

        assert result["success"] is True
        assert result["booking_id"] == booking.id
        assert result["user_id"] == 1
        assert result["room_id"] == 1
        assert result["attendees"] == 6
        assert result["status"] == "confirmed"

    finally:
        if booking is not None:
            db.delete(booking)
            db.commit()
        else:
            db.rollback()

        db.close()

def test_dispatch_cancel_booking():
    db = SessionLocal()
    booking = None

    try:
        booking = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2031, 4, 2, 10, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2031, 4, 2, 11, 0,
                tzinfo=timezone.utc,
            ),
            attendees=5,
        )

        result = dispatch_tool(
            tool_name="cancel_booking",
            arguments={
                "booking_id": booking.id,
                "user_id": 1,
            },
            db=db,
        )

        assert result["success"] is True
        assert result["booking_id"] == booking.id
        assert result["user_id"] == 1
        assert result["status"] == "cancelled"

    finally:
        if booking is not None:
            db.delete(booking)
            db.commit()
        else:
            db.rollback()

        db.close()


def test_dispatch_authenticated_user_overrides_model_user_id():
    db = SessionLocal()

    try:
        result = dispatch_tool(
            tool_name="view_bookings",
            arguments={
                "user_id": 2,
            },
            db=db,
            authenticated_user_id=1,
        )

        assert result["success"] is True
        assert result["user_id"] == 1


    finally:
        db.close()

def test_dispatch_batch_move_bookings():
    db = SessionLocal()
    booking = None

    try:
        booking = create_booking(
            db=db,
            user_id=1,
            room_id=1,
            start_time=datetime(
                2031, 3, 9, 18, 0,
                tzinfo=timezone.utc,
            ),
            end_time=datetime(
                2031, 3, 9, 19, 0,
                tzinfo=timezone.utc,
            ),
            attendees=6,
        )

        result = dispatch_tool(
            tool_name="batch_move_bookings",
            arguments={
                "user_id": 1,
                "moves": [
                    {
                        "booking_id": booking.id,
                        "room_id": 1,
                        "start_time": "2031-03-10T18:00:00Z",
                        "end_time": "2031-03-10T19:00:00Z",
                        "attendees": 6,
                    }
                ],
            },
            db=db,
            authenticated_user_id=1,
        )

        assert result["success"] is True
        assert result["user_id"] == 1
        assert result["moved_count"] == 1
        assert result["bookings"][0]["booking_id"] == booking.id

    finally:
        if booking is not None:
            db.delete(booking)
            db.commit()
        else:
            db.rollback()

        db.close()

        
def test_dispatch_invalid_tool_arguments_return_validation_error():
    db = SessionLocal()

    try:
        result = dispatch_tool(
            tool_name="book_room",
            arguments={
                "user_id": 1,
                "room_id": "bad",
                "start_time": "bad",
                "end_time": "bad",
                "attendees": -2,
            },
            db=db,
            authenticated_user_id=1,
        )

        assert result["success"] is False
        assert result["error_type"] == "validation_error"

        error_locations = {
            detail["loc"][0]
            for detail in result["details"]
        }

        assert "room_id" in error_locations
        assert "start_time" in error_locations
        assert "end_time" in error_locations
        assert "attendees" in error_locations

    finally:
        db.close()