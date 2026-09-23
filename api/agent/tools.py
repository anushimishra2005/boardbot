from datetime import datetime

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.services.availability_service import check_room_availability
from api.services.booking_service import (
    batch_move_bookings,
    create_booking,
    list_bookings,
    update_booking,
    cancel_booking,
)
from sqlalchemy import select

from api.models.room import Room
from api.models.equipment import Equipment
from api.models.room_equipment import RoomEquipment


class BookRoomInput(BaseModel):
    user_id: int = Field(gt=0)
    room_id: int = Field(gt=0)
    start_time: datetime
    end_time: datetime
    attendees: int = Field(gt=0)


def book_room(
    db: Session,
    data: BookRoomInput,
) -> dict:
    """Validate and create a room booking."""

    if data.start_time >= data.end_time:
        raise ValueError("Start time must be before end time.")

    booking = create_booking(
        db=db,
        user_id=data.user_id,
        room_id=data.room_id,
        start_time=data.start_time,
        end_time=data.end_time,
        attendees=data.attendees,
    )

    return {
        "success": True,
        "booking_id": booking.id,
        "user_id": booking.user_id,
        "room_id": booking.room_id,
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "attendees": booking.attendees,
        "status": booking.status,
    }

class CheckAvailabilityInput(BaseModel):
    room_id: int = Field(gt=0)
    start_time: datetime
    end_time: datetime


def check_availability(
    db: Session,
    data: CheckAvailabilityInput,
) -> dict:
    """Check whether a room is available for a requested time range."""

    if data.start_time >= data.end_time:
        raise ValueError(
            "Start time must be before end time."
        )

    available = check_room_availability(
        db=db,
        room_id=data.room_id,
        start_time=data.start_time,
        end_time=data.end_time,
    )

    return {
        "room_id": data.room_id,
        "start_time": data.start_time.isoformat(),
        "end_time": data.end_time.isoformat(),
        "available": available,
    }
from sqlalchemy import select

from api.models.room import Room


class RecommendRoomInput(BaseModel):
    attendees: int = Field(gt=0)
    required_equipment: list[str] = Field(default_factory=list)


def recommend_room(
    db: Session,
    data: RecommendRoomInput,
) -> dict:
    """Recommend rooms based on capacity and required equipment."""

    rooms = db.execute(
        select(Room)
        .order_by(Room.capacity.asc())
    ).scalars().all()

    recommendations = []

    for room in rooms:
        if room.capacity < data.attendees:
            continue

        room_equipment = {
            equipment.name.lower()
            for equipment in room.equipment
        }

        required = {
            item.strip().lower()
            for item in data.required_equipment
        }

        if not required.issubset(room_equipment):
            continue

        recommendations.append(
            {
                "room_id": room.id,
                "name": room.name,
                "capacity": room.capacity,
                "floor": room.floor,
                "equipment": sorted(room_equipment),
            }
        )

    return {
        "success": True,
        "requested_attendees": data.attendees,
        "required_equipment": data.required_equipment,
        "recommendations": recommendations,
    }
class RecommendRoomInput(BaseModel):
    attendees: int = Field(gt=0)
    required_equipment: list[str] = Field(default_factory=list)


def recommend_room(
    db: Session,
    data: RecommendRoomInput,
) -> dict:
    """Recommend rooms based on capacity and required equipment."""

    rooms = db.execute(
        select(Room).order_by(Room.capacity.asc())
    ).scalars().all()

    recommendations = []

    required = {
        item.strip().lower()
        for item in data.required_equipment
    }

    for room in rooms:
        if room.capacity < data.attendees:
            continue

        equipment_rows = db.execute(
            select(Equipment.name)
            .join(
                RoomEquipment,
                RoomEquipment.equipment_id == Equipment.id,
            )
            .where(RoomEquipment.room_id == room.id)
        ).all()

        room_equipment = {
            row[0].strip().lower()
            for row in equipment_rows
        }

        if not required.issubset(room_equipment):
            continue

        recommendations.append(
            {
                "room_id": room.id,
                "name": room.name,
                "capacity": room.capacity,
                "location": room.location,
                "equipment": sorted(room_equipment),
            }
        )

    return {
        "success": True,
        "requested_attendees": data.attendees,
        "required_equipment": data.required_equipment,
        "recommendations": recommendations,
    }
class ViewBookingsInput(BaseModel):
    user_id: int = Field(gt=0)


def view_bookings(
    db: Session,
    data: ViewBookingsInput,
) -> dict:
    """Return all bookings belonging to a user."""

    bookings = list_bookings(
        db=db,
        user_id=data.user_id,
    )

    return {
        "success": True,
        "user_id": data.user_id,
        "bookings": [
            {
                "booking_id": booking.id,
                "room_id": booking.room_id,
                "start_time": booking.start_time.isoformat(),
                "end_time": booking.end_time.isoformat(),
                "attendees": booking.attendees,
                "status": booking.status,
            }
            for booking in bookings
        ],
    }
class EditBookingInput(BaseModel):
    booking_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    room_id: int = Field(gt=0)
    start_time: datetime
    end_time: datetime
    attendees: int = Field(gt=0)


def edit_booking(
    db: Session,
    data: EditBookingInput,
) -> dict:
    """Update an existing booking belonging to the user."""

    if data.start_time >= data.end_time:
        raise ValueError("Start time must be before end time.")

    booking = update_booking(
        db=db,
        booking_id=data.booking_id,
        room_id=data.room_id,
        start_time=data.start_time,
        end_time=data.end_time,
        attendees=data.attendees,
        user_id=data.user_id,
    )

    return {
        "success": True,
        "booking_id": booking.id,
        "user_id": booking.user_id,
        "room_id": booking.room_id,
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "attendees": booking.attendees,
        "status": booking.status,
    }
class CancelBookingInput(BaseModel):
    booking_id: int = Field(gt=0)
    user_id: int = Field(gt=0)


def cancel_booking_tool(
    db: Session,
    data: CancelBookingInput,
) -> dict:
    """Cancel an existing booking belonging to the user."""

    booking = cancel_booking(
        db=db,
        booking_id=data.booking_id,
        user_id=data.user_id,
    )

    return {
        "success": True,
        "booking_id": booking.id,
        "user_id": booking.user_id,
        "room_id": booking.room_id,
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "attendees": booking.attendees,
        "status": booking.status,
    }
class BatchMoveItem(BaseModel):
    booking_id: int = Field(gt=0)
    room_id: int = Field(gt=0)
    start_time: datetime
    end_time: datetime
    attendees: int = Field(gt=0)


class BatchMoveBookingsInput(BaseModel):
    user_id: int = Field(gt=0)
    moves: list[BatchMoveItem] = Field(min_length=1)


def batch_move_bookings_tool(
    db: Session,
    data: BatchMoveBookingsInput,
) -> dict:
    """Move multiple bookings atomically."""

    for move in data.moves:
        if move.start_time >= move.end_time:
            raise ValueError(
                f"Start time must be before end time for booking "
                f"{move.booking_id}."
            )

    updated_bookings = batch_move_bookings(
        db=db,
        user_id=data.user_id,
        moves=[
            {
                "booking_id": move.booking_id,
                "room_id": move.room_id,
                "start_time": move.start_time,
                "end_time": move.end_time,
                "attendees": move.attendees,
            }
            for move in data.moves
        ],
    )

    return {
        "success": True,
        "user_id": data.user_id,
        "moved_count": len(updated_bookings),
        "bookings": [
            {
                "booking_id": booking.id,
                "room_id": booking.room_id,
                "start_time": booking.start_time.isoformat(),
                "end_time": booking.end_time.isoformat(),
                "attendees": booking.attendees,
                "status": booking.status,
            }
            for booking in updated_bookings
        ],
    }