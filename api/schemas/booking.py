from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


class BookingCreate(BaseModel):
    room_id: int
    start_time: datetime
    end_time: datetime
    attendees: int = Field(gt=0)

    _normalize_start_time = field_validator(
        "start_time",
        mode="after",
    )(normalize_datetime)

    _normalize_end_time = field_validator(
        "end_time",
        mode="after",
    )(normalize_datetime)


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

    _normalize_start_time = field_validator(
        "start_time",
        mode="after",
    )(normalize_datetime)

    _normalize_end_time = field_validator(
        "end_time",
        mode="after",
    )(normalize_datetime)