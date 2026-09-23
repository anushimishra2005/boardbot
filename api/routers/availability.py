from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.core.dependencies import get_db
from api.schemas.availability import AvailabilityResponse
from api.services.availability_service import check_room_availability


router = APIRouter(
    prefix="/availability",
    tags=["availability"],
)


@router.get(
    "",
    response_model=AvailabilityResponse,
)
def check_availability(
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db),
):
    available = check_room_availability(
        db=db,
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
    )

    return AvailabilityResponse(
        room_id=room_id,
        start_time=start_time,
        end_time=end_time,
        available=available,
    )