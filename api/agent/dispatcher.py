from datetime import datetime

from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.agent.tools import (
    CheckAvailabilityInput,
    check_availability,
    BookRoomInput,
    book_room,
    RecommendRoomInput,
    recommend_room,
    ViewBookingsInput,
    view_bookings,
    EditBookingInput,
    edit_booking,
    CancelBookingInput,
    cancel_booking_tool,
    BatchMoveBookingsInput,
    batch_move_bookings_tool,
)


def dispatch_tool(
    tool_name: str,
    arguments: dict,
    db: Session,
    authenticated_user_id: int | None = None,
) -> dict:
    """Validate and execute a BoardBot tool call."""

    try:
        if tool_name == "check_availability":
            data = CheckAvailabilityInput(
                room_id=arguments["room_id"],
                start_time=datetime.fromisoformat(
                    arguments["start_time"].replace("Z", "+00:00")
                ),
                end_time=datetime.fromisoformat(
                    arguments["end_time"].replace("Z", "+00:00")
                ),
            )

            return check_availability(
                db=db,
                data=data,
            )

        if tool_name == "book_room":
            data = BookRoomInput(
                user_id=(
                    authenticated_user_id
                    if authenticated_user_id is not None
                    else arguments["user_id"]
                ),
                room_id=arguments["room_id"],
                start_time=datetime.fromisoformat(
                    arguments["start_time"].replace("Z", "+00:00")
                ),
                end_time=datetime.fromisoformat(
                    arguments["end_time"].replace("Z", "+00:00")
                ),
                attendees=arguments["attendees"],
            )

            return book_room(
                db=db,
                data=data,
            )

        if tool_name == "recommend_room":
            data = RecommendRoomInput(
                attendees=arguments["attendees"],
                required_equipment=arguments.get(
                    "required_equipment",
                    [],
                ),
            )

            return recommend_room(
                db=db,
                data=data,
            )

        if tool_name == "view_bookings":
            data = ViewBookingsInput(
                user_id=(
                    authenticated_user_id
                    if authenticated_user_id is not None
                    else arguments["user_id"]
                ),
            )

            return view_bookings(
                db=db,
                data=data,
            )

        if tool_name == "edit_booking":
            data = EditBookingInput(
                booking_id=arguments["booking_id"],
                user_id=arguments["user_id"],
                room_id=arguments["room_id"],
                start_time=datetime.fromisoformat(
                    arguments["start_time"].replace("Z", "+00:00")
                ),
                end_time=datetime.fromisoformat(
                    arguments["end_time"].replace("Z", "+00:00")
                ),
                attendees=arguments["attendees"],
            )

            return edit_booking(
                db=db,
                data=data,
            )

        if tool_name == "cancel_booking":
            data = CancelBookingInput(
                booking_id=arguments["booking_id"],
                user_id=arguments["user_id"],
            )

            return cancel_booking_tool(
                db=db,
                data=data,
            )
        if tool_name == "batch_move_bookings":
            data = BatchMoveBookingsInput(
                user_id=(
                    authenticated_user_id
                    if authenticated_user_id is not None
                    else arguments["user_id"]
                ),
                moves=arguments["moves"],
            )

            return batch_move_bookings_tool(
                db=db,
                data=data,
            )
        raise ValueError(f"Unknown tool: {tool_name}")

    except ValidationError as exc:
        return {
            "success": False,
            "error_type": "validation_error",
            "message": "The tool arguments failed validation.",
            "details": exc.errors(),
        }

    except ValueError as exc:
        return {
            "success": False,
            "error_type": "tool_error",
            "message": str(exc),
        }