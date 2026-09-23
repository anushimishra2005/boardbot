class AgentContext:
    """Stores short-lived conversation state for a BoardBot session."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.last_tool_name: str | None = None
        self.last_tool_result: dict | None = None
        self.last_booking_id: int | None = None
        self.pending_action: str | None = None
        self.pending_arguments: dict | None = None

    def remember_tool_result(
        self,
        tool_name: str,
        result: dict,
    ) -> None:
        self.last_tool_name = tool_name
        self.last_tool_result = result

        if result.get("booking_id") is not None:
            self.last_booking_id = result["booking_id"]
    def set_pending_action(
        self,
        tool_name: str,
        arguments: dict,
    ) -> None:
        """Store a mutation that is waiting for user confirmation."""

        self.pending_action = tool_name
        self.pending_arguments = arguments


    def clear_pending_action(self) -> None:
        """Clear any mutation waiting for confirmation."""

        self.pending_action = None
        self.pending_arguments = None
    def resolve_booking_reference(
        self,
        reference: str,
    ) -> int | None:
        """Resolve simple conversational booking references."""

        normalized = reference.strip().lower()

        if normalized in {
            "that booking",
            "this booking",
            "the booking",
            "that one",
            "this one",
        }:
            return self.last_booking_id

        return None