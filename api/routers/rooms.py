from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.dependencies import get_db
from api.schemas.room import RoomResponse
from api.services.room_service import get_room, list_rooms


router = APIRouter(
    prefix="/rooms",
    tags=["rooms"],
)


@router.get(
    "",
    response_model=list[RoomResponse],
)
def get_rooms(
    db: Session = Depends(get_db),
):
    return list_rooms(db)


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
)
def get_room_by_id(
    room_id: int,
    db: Session = Depends(get_db),
):
    room = get_room(
        db=db,
        room_id=room_id,
    )

    if room is None:
        raise HTTPException(
            status_code=404,
            detail=f"Room with ID {room_id} not found.",
        )

    return room