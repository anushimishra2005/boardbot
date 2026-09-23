from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.dependencies import get_current_user, get_db
from api.models.user import User
from api.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingUpdate,
)

from api.services.booking_service import (
    cancel_booking,
    create_booking,
    get_booking,
    list_bookings,
    update_booking,
)


router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


@router.post(
    "",
    response_model=BookingResponse,
    status_code=201,
)
def create_new_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        booking = create_booking(
            db=db,
            user_id=current_user.id,
            room_id=booking_data.room_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            attendees=booking_data.attendees,
        )

        return booking

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get(
    "",
    response_model=list[BookingResponse],
)
def get_bookings(
    db: Session = Depends(get_db),
):
    return list_bookings(db)


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
)
def get_booking_by_id(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = get_booking(
        db=db,
        booking_id=booking_id,
        user_id=current_user.id,
    )

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail=f"Booking with ID {booking_id} not found.",
        )

    return booking
@router.patch(
    "/{booking_id}",
    response_model=BookingResponse,
)
def update_existing_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        booking = update_booking(
            db=db,
            booking_id=booking_id,
            room_id=booking_data.room_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            attendees=booking_data.attendees,
            user_id=current_user.id,
        )

        return booking

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
@router.delete(
    "/{booking_id}",
    response_model=BookingResponse,
)
def cancel_existing_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        booking = cancel_booking(
            db=db,
            booking_id=booking_id,
            user_id=current_user.id,
        )

        return booking

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )