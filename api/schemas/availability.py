from datetime import datetime

from pydantic import BaseModel


class AvailabilityResponse(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime
    available: bool