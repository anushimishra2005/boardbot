from google import genai

from api.core.config import settings

from api.agent.tool_schemas import (
    CHECK_AVAILABILITY_TOOL,
    BOOK_ROOM_TOOL,
    RECOMMEND_ROOM_TOOL,
    VIEW_BOOKINGS_TOOL,
    EDIT_BOOKING_TOOL,
    CANCEL_BOOKING_TOOL,
    BATCH_MOVE_BOOKINGS_TOOL,
)

MODEL_NAME = "gemini-3.8-flash"


class GeminiProvider:
    """Thin wrapper around the Gemini Interactions API."""

    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = MODEL_NAME
        self.tools = [
            CHECK_AVAILABILITY_TOOL,
            BOOK_ROOM_TOOL,
            RECOMMEND_ROOM_TOOL,
            VIEW_BOOKINGS_TOOL,
            EDIT_BOOKING_TOOL,
            CANCEL_BOOKING_TOOL,
            BATCH_MOVE_BOOKINGS_TOOL,
        ]

    def request_tool_call(self, user_message: str):
        """Ask Gemini to interpret a user request and optionally call a tool."""

        return self.client.interactions.create(
            model=self.model_name,
            input=user_message,
            tools=self.tools,
        )
    def continue_interaction(self, interaction_id: str, function_results: list):
        """Continue a Gemini interaction with tool results."""
        
        return self.client.interactions.create(
            model=self.model_name,
            previous_interaction_id=interaction_id,
            input=function_results,
            tools=self.tools,
        )