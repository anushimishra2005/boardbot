from datetime import datetime, time, timezone


BUSINESS_START = time(9, 0)
BUSINESS_END = time(21, 0)


def validate_time_range(
    start_time: datetime,
    end_time: datetime,
) -> tuple[bool, str | None]:
    """Validate that the booking has a valid chronological time range."""

    if start_time >= end_time:
        return False, "Start time must be before end time."

    return True, None


def validate_business_hours(
    start_time: datetime,
    end_time: datetime,
) -> tuple[bool, str | None]:
    """Ensure the booking falls within 09:00–21:00."""

    start = start_time.timetz().replace(tzinfo=None)
    end = end_time.timetz().replace(tzinfo=None)

    if start < BUSINESS_START or end > BUSINESS_END:
        return False, "Bookings must be between 09:00 and 21:00."

    return True, None


def validate_not_in_past(
    start_time: datetime,
) -> tuple[bool, str | None]:
    """Prevent bookings from starting in the past."""

    now = datetime.now(timezone.utc)

    if start_time < now:
        return False, "Booking cannot start in the past."

    return True, None
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
def validate_equipment(
    required_equipment: set[str],
    room_equipment: set[str],
) -> tuple[bool, str | None]:
    """Ensure the room has all required equipment."""

    missing_equipment = required_equipment - room_equipment

    if missing_equipment:
        missing = ", ".join(sorted(missing_equipment))
        return False, f"Room is missing required equipment: {missing}."

    return True, None
def validate_no_overlap(
    new_start: datetime,
    new_end: datetime,
    existing_start: datetime,
    existing_end: datetime,
) -> tuple[bool, str | None]:
    """Ensure a new booking does not overlap an existing booking."""

    if new_start < existing_end and new_end > existing_start:
        return False, "The requested time overlaps with an existing booking."

    return True, None