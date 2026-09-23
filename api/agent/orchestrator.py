import json

from sqlalchemy.orm import Session

from api.agent.dispatcher import dispatch_tool
from api.agent.gemini_provider import GeminiProvider

from api.agent.context import AgentContext
MUTATING_TOOLS = {
    "book_room",
    "edit_booking",
    "cancel_booking",
    "batch_move_bookings",
}

def requires_confirmation(tool_name: str) -> bool:
    return tool_name in MUTATING_TOOLS
def build_confirmation_message(
    tool_name: str,
    arguments: dict,
) -> str:
    if tool_name == "book_room":
        return (
            f"You're about to book room {arguments['room_id']} "
            f"from {arguments['start_time']} to "
            f"{arguments['end_time']} for "
            f"{arguments['attendees']} attendees. "
            "Shall I proceed?"
        )

    if tool_name == "edit_booking":
        return (
            f"You're about to move booking {arguments['booking_id']} "
            f"to room {arguments['room_id']} from "
            f"{arguments['start_time']} to {arguments['end_time']} "
            f"for {arguments['attendees']} attendees. "
            "Shall I proceed?"
        )
    if tool_name == "cancel_booking":
        return (
            f"You're about to cancel booking "
            f"{arguments['booking_id']}. "
            "This will remove the booking from the active schedule. "
            "Shall I proceed?"
        )
    if tool_name == "batch_move_bookings":
        moves = arguments.get("moves", [])

        return (
            f"You're about to move {len(moves)} booking"
            f"{'' if len(moves) == 1 else 's'} "
            "as part of a batch operation. "
            "Shall I proceed?"
        )

    

    return (
        f"You're about to execute {tool_name.replace('_', ' ')}. "
        "Shall I proceed?"
    )

def is_confirmation_message(message: str) -> bool:
    normalized = message.strip().lower()

    exact_matches = {
        "yes",
        "y",
        "confirm",
        "confirmed",
        "go ahead",
        "do it",
        "proceed",
    }

    if normalized in exact_matches:
        return True

    confirmation_prefixes = (
        "yes,",
        "yes ",
        "yeah,",
        "yeah ",
        "yep,",
        "yep ",
        "sure,",
        "sure ",
        "okay,",
        "okay ",
        "ok,",
        "ok ",
    )

    return normalized.startswith(confirmation_prefixes)


def is_rejection_message(message: str) -> bool:
    normalized = message.strip().lower()

    exact_matches = {
        "no",
        "n",
        "cancel",
        "don't",
        "do not",
        "never mind",
        "nevermind",
    }

    if normalized in exact_matches:
        return True

    rejection_prefixes = (
        "no,",
        "no ",
        "nah,",
        "nah ",
        "don't ",
        "do not ",
        "never mind,",
        "nevermind,",
    )

    return normalized.startswith(rejection_prefixes)


class BoardBotOrchestrator:
    """Coordinates Gemini reasoning and deterministic tool execution."""

    def __init__(self, user_id: int) -> None:
        self.provider = GeminiProvider()
        self.context = AgentContext(user_id)
    def confirm_pending_action(self, db: Session) -> str:
        """Execute the pending mutation after explicit user confirmation."""

        if (
            self.context.pending_action is None
            or self.context.pending_arguments is None
        ):
            return "There is no pending action to confirm."

        tool_name = self.context.pending_action
        arguments = self.context.pending_arguments

        tool_result = dispatch_tool(
            tool_name=tool_name,
            arguments=arguments,
            db=db,
            authenticated_user_id=self.context.user_id,
        )

        self.context.clear_pending_action()
        self.context.remember_tool_result(
            tool_name=tool_name,
            result=tool_result,
        )

        if not tool_result.get("success", False):
            return tool_result.get(
                "message",
                "I couldn't complete the requested action.",
            )

        return f"{tool_name.replace('_', ' ').capitalize()} completed successfully."
    def chat(self, user_message: str, db: Session) -> str:
        """Process a user message and return BoardBot's final response."""
        if self.context.pending_action is not None:
            if is_confirmation_message(user_message):
                return self.confirm_pending_action(db)

            if is_rejection_message(user_message):
                self.context.clear_pending_action()
                return "Okay, I cancelled that action."

            return (
                "I still need your confirmation. "
                "Please reply yes to proceed or no to cancel."
            )
        interaction = self.provider.request_tool_call(user_message)

        for _ in range(3):
            function_calls = [
                step
                for step in interaction.steps
                if step.type == "function_call"
            ]

            if not function_calls:
                return (
                    interaction.output_text
                    or "I couldn't determine a response."
                )

            function_results = []

            for function_call in function_calls:
                if requires_confirmation(function_call.name):
                    self.context.set_pending_action(
                        tool_name=function_call.name,
                        arguments=function_call.arguments,
                    )

                    return build_confirmation_message(
                        tool_name=function_call.name,
                        arguments=function_call.arguments,
                    )

                tool_result = dispatch_tool(
                    tool_name=function_call.name,
                    arguments=function_call.arguments,
                    db=db,
                    authenticated_user_id=self.context.user_id,
                )
                self.context.remember_tool_result(
                    tool_name=function_call.name,
                    result=tool_result,
                )

                function_results.append(
                    {
                        "type": "function_result",
                        "name": function_call.name,
                        "call_id": function_call.id,
                        "result": [
                            {
                                "type": "text",
                                "text": json.dumps(tool_result),
                            }
                        ],
                    }
                )

            interaction = self.provider.continue_interaction(
                interaction_id=interaction.id,
                function_results=function_results,
            )
        return "I couldn't complete the request after several tool steps."