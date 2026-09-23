from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BookingCreate(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime
    attendees: int = Field(gt=0)


class BookingResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    attendees: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BookingUpdate(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime
    attendees: int = Field(gt=0)