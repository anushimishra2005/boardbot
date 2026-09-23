from datetime import datetime, timezone

from api.services.scheduling_engine import (
    validate_business_hours,
    validate_not_in_past,
    validate_time_range,
    validate_capacity,
    validate_equipment,
    validate_no_overlap,
)


def test_valid_time_range():
    start = datetime(2027, 1, 10, 10, 0, tzinfo=timezone.utc)
    end = datetime(2027, 1, 10, 11, 0, tzinfo=timezone.utc)

    valid, error = validate_time_range(start, end)

    assert valid is True
    assert error is None


def test_invalid_time_range():
    start = datetime(2027, 1, 10, 12, 0, tzinfo=timezone.utc)
    end = datetime(2027, 1, 10, 11, 0, tzinfo=timezone.utc)

    valid, error = validate_time_range(start, end)

    assert valid is False
    assert error == "Start time must be before end time."


def test_business_hours():
    start = datetime(2027, 1, 10, 10, 0, tzinfo=timezone.utc)
    end = datetime(2027, 1, 10, 11, 0, tzinfo=timezone.utc)

    valid, error = validate_business_hours(start, end)

    assert valid is True
    assert error is None


def test_outside_business_hours():
    start = datetime(2027, 1, 10, 8, 0, tzinfo=timezone.utc)
    end = datetime(2027, 1, 10, 10, 0, tzinfo=timezone.utc)

    valid, error = validate_business_hours(start, end)

    assert valid is False
    assert error == "Bookings must be between 09:00 and 21:00."


def test_past_booking():
    start = datetime(2020, 1, 1, 10, 0, tzinfo=timezone.utc)

    valid, error = validate_not_in_past(start)

    assert valid is False
    assert error == "Booking cannot start in the past."
def validate_capacity(
    attendees: int,
    room_capacity: int,
) -> tuple[bool, str | None]:
    """Ensure the room can accommodate all attendees."""

    if attendees <= 0:
        return False, "Attendee count must be greater than zero."

    if attendees > room_capacity:
        return (
            False,
            f"Room capacity is {room_capacity}, "
            f"but {attendees} attendees were requested.",
        )

    return True, None
def test_validate_capacity_valid():
    valid, error = validate_capacity(
        attendees=8,
        room_capacity=10,
    )

    assert valid is True
    assert error is None


def test_validate_capacity_exceeded():
    valid, error = validate_capacity(
        attendees=12,
        room_capacity=10,
    )

    assert valid is False
    assert error == "Room capacity is 10, but 12 attendees were requested."
def test_validate_equipment_available():
    valid, error = validate_equipment(
        required_equipment={"projector", "whiteboard"},
        room_equipment={"projector", "whiteboard", "video conferencing"},
    )

    assert valid is True
    assert error is None


def test_validate_equipment_missing():
    valid, error = validate_equipment(
        required_equipment={"projector", "whiteboard"},
        room_equipment={"projector"},
    )

    assert valid is False
    assert error == "Room is missing required equipment: whiteboard."

def test_validate_no_overlap_when_times_overlap():
    valid, error = validate_no_overlap(
        new_start=datetime(2026, 9, 21, 10, 30),
        new_end=datetime(2026, 9, 21, 11, 30),
        existing_start=datetime(2026, 9, 21, 10, 0),
        existing_end=datetime(2026, 9, 21, 11, 0),
    )

    assert valid is False
    assert error == "The requested time overlaps with an existing booking."


def test_validate_no_overlap_when_times_do_not_overlap():
    valid, error = validate_no_overlap(
        new_start=datetime(2026, 9, 21, 11, 0),
        new_end=datetime(2026, 9, 21, 12, 0),
        existing_start=datetime(2026, 9, 21, 10, 0),
        existing_end=datetime(2026, 9, 21, 11, 0),
    )

    assert valid is True
    assert error is None