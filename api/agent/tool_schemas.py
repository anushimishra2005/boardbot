CHECK_AVAILABILITY_TOOL = {
    "type": "function",
    "name": "check_availability",
    "description": (
        "Check whether a specific meeting room is available "
        "during a requested time range."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "room_id": {
                "type": "integer",
                "description": "The ID of the room to check.",
            },
            "start_time": {
                "type": "string",
                "description": (
                    "The requested start time as an ISO 8601 "
                    "datetime with timezone."
                ),
            },
            "end_time": {
                "type": "string",
                "description": (
                    "The requested end time as an ISO 8601 "
                    "datetime with timezone."
                ),
            },
        },
        "required": [
            "room_id",
            "start_time",
            "end_time",
        ],
        "additionalProperties": False,
    },
}
BOOK_ROOM_TOOL = {
    "type": "function",
    "name": "book_room",
    "description": (
        "Create a meeting room booking for a user. "
        "Use this only when the user has provided a specific room, "
        "start time, end time, and attendee count."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "ID of the user making the booking.",
            },
            "room_id": {
                "type": "integer",
                "description": "ID of the room to book.",
            },
            "start_time": {
                "type": "string",
                "description": (
                    "Booking start as an ISO 8601 datetime "
                    "with timezone."
                ),
            },
            "end_time": {
                "type": "string",
                "description": (
                    "Booking end as an ISO 8601 datetime "
                    "with timezone."
                ),
            },
            "attendees": {
                "type": "integer",
                "description": "Number of people attending.",
            },
        },
        "required": [
            "user_id",
            "room_id",
            "start_time",
            "end_time",
            "attendees",
        ],
        "additionalProperties": False,
    },
}
RECOMMEND_ROOM_TOOL = {
    "type": "function",
    "name": "recommend_room",
    "description": (
        "Recommend meeting rooms based on the number of attendees "
        "and required equipment. Use this when the user has not "
        "specified a particular room and wants a suitable room "
        "recommendation."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "attendees": {
                "type": "integer",
                "description": "Number of people attending the meeting.",
            },
            "required_equipment": {
                "type": "array",
                "items": {
                    "type": "string",
                },
                "description": (
                    "Equipment required in the room, such as "
                    "projector, whiteboard, speaker, or "
                    "video conferencing."
                ),
            },
        },
        "required": ["attendees", "required_equipment"],
        "additionalProperties": False,
    },
}
VIEW_BOOKINGS_TOOL = {
    "type": "function",
    "name": "view_bookings",
    "description": (
        "View the bookings belonging to a specific user. "
        "Use this when the user asks to see their bookings, "
        "meetings, reservations, or scheduled room bookings."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "ID of the user whose bookings should be retrieved.",
            },
        },
        "required": ["user_id"],
        "additionalProperties": False,
    },
}
EDIT_BOOKING_TOOL = {
    "type": "function",
    "name": "edit_booking",
    "description": (
        "Update an existing room booking. Use this when the user "
        "wants to change the room, time, or attendee count of an "
        "existing booking."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "booking_id": {
                "type": "integer",
                "description": "ID of the booking to update.",
            },
            "user_id": {
                "type": "integer",
                "description": "ID of the user who owns the booking.",
            },
            "room_id": {
                "type": "integer",
                "description": "ID of the new room.",
            },
            "start_time": {
                "type": "string",
                "description": (
                    "New booking start as an ISO 8601 datetime "
                    "with timezone."
                ),
            },
            "end_time": {
                "type": "string",
                "description": (
                    "New booking end as an ISO 8601 datetime "
                    "with timezone."
                ),
            },
            "attendees": {
                "type": "integer",
                "description": "New number of attendees.",
            },
        },
        "required": [
            "booking_id",
            "user_id",
            "room_id",
            "start_time",
            "end_time",
            "attendees",
        ],
        "additionalProperties": False,
    },
}
CANCEL_BOOKING_TOOL = {
    "type": "function",
    "name": "cancel_booking",
    "description": (
        "Cancel an existing room booking. Use this when the user "
        "wants to cancel a specific booking."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "booking_id": {
                "type": "integer",
                "description": "ID of the booking to cancel.",
            },
            "user_id": {
                "type": "integer",
                "description": "ID of the user who owns the booking.",
            },
        },
        "required": [
            "booking_id",
            "user_id",
        ],
        "additionalProperties": False,
    },
}

BATCH_MOVE_BOOKINGS_TOOL = {
    "type": "function",
    "name": "batch_move_bookings",
    "description": (
        "Move multiple existing room bookings to new rooms or times "
        "in one atomic operation. Use this when the user wants to "
        "reschedule or move multiple bookings together."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "ID of the user who owns the bookings.",
            },
            "moves": {
                "type": "array",
                "description": "The bookings to move and their new details.",
                "items": {
                    "type": "object",
                    "properties": {
                        "booking_id": {
                            "type": "integer",
                            "description": "ID of the booking to move.",
                        },
                        "room_id": {
                            "type": "integer",
                            "description": "ID of the new room.",
                        },
                        "start_time": {
                            "type": "string",
                            "description": (
                                "New booking start as an ISO 8601 "
                                "datetime with timezone."
                            ),
                        },
                        "end_time": {
                            "type": "string",
                            "description": (
                                "New booking end as an ISO 8601 "
                                "datetime with timezone."
                            ),
                        },
                        "attendees": {
                            "type": "integer",
                            "description": "Number of attendees.",
                        },
                    },
                    "required": [
                        "booking_id",
                        "room_id",
                        "start_time",
                        "end_time",
                        "attendees",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": [
            "user_id",
            "moves",
        ],
        "additionalProperties": False,
    },
}