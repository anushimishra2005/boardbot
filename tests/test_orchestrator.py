from types import SimpleNamespace

from api.agent.orchestrator import (
    BoardBotOrchestrator,
    build_confirmation_message,
    is_confirmation_message,
    is_rejection_message,
    requires_confirmation,
)
from api.core.database import SessionLocal
from api.agent.context import AgentContext
from api.models import Booking

class FakeInteractions:
    def create(
        self,
        model,
        previous_interaction_id,
        input,
        tools,
    ):
        assert previous_interaction_id in {
            "interaction_123",
            "interaction_error",
        }

        function_result = input[0]

        assert function_result["type"] == "function_result"
        assert function_result["name"] == "check_availability"

        return SimpleNamespace(
            output_text="Room 1 is available.",
            steps=[],
            id="interaction_456",
        )


class FakeClient:
    def __init__(self):
        self.interactions = FakeInteractions()


class FakeProvider:
    def __init__(self):
        self.model_name = "fake-model"
        self.tools = []
        self.client = FakeClient()

    def request_tool_call(self, user_message):
        function_call = SimpleNamespace(
            type="function_call",
            name="check_availability",
            id="call_123",
            arguments={
                "room_id": 1,
                "start_time": "2090-02-01T15:00:00Z",
                "end_time": "2090-02-01T16:00:00Z",
            },
        )

        return SimpleNamespace(
            steps=[function_call],
            output_text=None,
            id="interaction_123",
        )

    def continue_interaction(
        self,
        interaction_id,
        function_results,
    ):
        return self.client.interactions.create(
            model=self.model_name,
            previous_interaction_id=interaction_id,
            input=function_results,
            tools=self.tools,
        )

def test_orchestrator_executes_tool_and_returns_final_response():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)
        orchestrator.provider = FakeProvider()

        result = orchestrator.chat(
            user_message="Is room 1 available?",
            db=db,
        )

        assert result == "Room 1 is available."

    finally:
        db.close()

def test_orchestrator_handles_tool_error():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)
        provider = FakeProvider()

        original_request = provider.request_tool_call

        def failed_tool_request(user_message):
            function_call = SimpleNamespace(
                type="function_call",
                name="check_availability",
                id="call_456",
                arguments={
                    "room_id": 999,
                    "start_time": "2090-03-01T15:00:00Z",
                    "end_time": "2090-03-01T16:00:00Z",
                },
            )

            return SimpleNamespace(
                steps=[function_call],
                output_text=None,
                id="interaction_error",
            )

        provider.request_tool_call = failed_tool_request

        orchestrator.provider = provider

        result = orchestrator.chat(
            user_message="Is room 999 available?",
            db=db,
        )

        assert result == "Room 1 is available."

    finally:
        db.close()

def test_orchestrator_handles_multiple_tool_steps():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)

        class MultiStepInteractions:
            def __init__(self):
                self.calls = 0

            def create(
                self,
                model,
                previous_interaction_id,
                input,
                tools,
            ):
                self.calls += 1

                if self.calls == 1:
                    return SimpleNamespace(
                        output_text=None,
                        steps=[
                            SimpleNamespace(
                                type="function_call",
                                name="check_availability",
                                id="call_1",
                                arguments={
                                    "room_id": 1,
                                    "start_time": "2035-03-01T15:00:00Z",
                                    "end_time": "2035-03-01T16:00:00Z",
                                },
                            )
                        ],
                        id="interaction_2",
                    )

                return SimpleNamespace(
                    output_text="The room is available and ready to book.",
                    steps=[],
                    id="interaction_3",
                )

        class MultiStepProvider(FakeProvider):
            def __init__(self):
                super().__init__()
                self.client = SimpleNamespace(
                    interactions=MultiStepInteractions()
                )

            def request_tool_call(self, user_message):
                return SimpleNamespace(
                    output_text=None,
                    steps=[
                        SimpleNamespace(
                            type="function_call",
                            name="recommend_room",
                            id="call_0",
                            arguments={
                                "attendees": 5,
                                "required_equipment": [
                                    "whiteboard"
                                ],
                            },
                        )
                    ],
                    id="interaction_1",
                )

        orchestrator.provider = MultiStepProvider()

        result = orchestrator.chat(
            user_message=(
                "Find a suitable room and check whether "
                "room 1 is available."
            ),
            db=db,
        )

        assert result == "The room is available and ready to book."

    finally:
        db.close()

def test_orchestrator_remembers_tool_result():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)

        result = {
            "success": True,
            "booking_id": 123,
            "status": "confirmed",
        }

        orchestrator.context.remember_tool_result(
            tool_name="book_room",
            result=result,
        )

        assert orchestrator.context.last_tool_name == "book_room"
        assert orchestrator.context.last_tool_result == result
        assert orchestrator.context.last_booking_id == 123

    finally:
        db.close()
def test_context_resolves_booking_reference():
    orchestrator = BoardBotOrchestrator(user_id=1)

    orchestrator.context.remember_tool_result(
        tool_name="book_room",
        result={
            "success": True,
            "booking_id": 123,
            "status": "confirmed",
        },
    )

    assert (
        orchestrator.context.resolve_booking_reference(
            "that booking"
        )
        == 123
    )

    assert (
        orchestrator.context.resolve_booking_reference(
            "this booking"
        )
        == 123
    )

    assert (
        orchestrator.context.resolve_booking_reference(
            "that one"
        )
        == 123
    )
def test_orchestrator_retries_validation_error_with_corrected_tool_call():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)

        class CorrectionInteractions:
            def __init__(self):
                self.calls = 0

            def create(
                self,
                model,
                previous_interaction_id,
                input,
                tools,
            ):
                self.calls += 1

                if self.calls == 1:
                    # First continuation receives the validation error.
                    result_text = input[0]["result"][0]["text"]

                    assert '"error_type": "validation_error"' in result_text

                    return SimpleNamespace(
                        output_text=None,
                        steps=[
                            SimpleNamespace(
                                type="function_call",
                                name="check_availability",
                                id="corrected_call",
                                arguments={
                                    "room_id": 1,
                                    "start_time": "2035-01-01T15:00:00Z",
                                    "end_time": "2035-01-01T16:00:00Z",
                                },
                            )
                        ],
                        id="interaction_corrected",
                    )

                return SimpleNamespace(
                    output_text="Room 1 is available after correcting the request.",
                    steps=[],
                    id="interaction_final",
                )

        class CorrectionProvider(FakeProvider):
            def __init__(self):
                super().__init__()
                self.client = SimpleNamespace(
                    interactions=CorrectionInteractions()
                )

            def request_tool_call(self, user_message):
                return SimpleNamespace(
                    output_text=None,
                    steps=[
                        SimpleNamespace(
                            type="function_call",
                            name="check_availability",
                            id="bad_call",
                            arguments={
                                "room_id": "bad",
                                "start_time": "bad",
                                "end_time": "bad",
                            },
                        )
                    ],
                    id="interaction_initial",
                )

        orchestrator.provider = CorrectionProvider()

        result = orchestrator.chat(
            user_message="Check room 1 availability.",
            db=db,
        )

        assert (
            result
            == "Room 1 is available after correcting the request."
        )

    finally:
        db.close()
def test_agent_context_tracks_and_clears_pending_action():
    context = AgentContext(user_id=1)

    arguments = {
        "room_id": 2,
        "start_time": "2035-01-01T15:00:00Z",
        "end_time": "2035-01-01T16:00:00Z",
        "attendees": 5,
    }

    context.set_pending_action(
        tool_name="book_room",
        arguments=arguments,
    )

    assert context.pending_action == "book_room"
    assert context.pending_arguments == arguments

    context.clear_pending_action()

    assert context.pending_action is None
    assert context.pending_arguments is None

def test_requires_confirmation_for_mutating_tools():
    assert requires_confirmation("book_room") is True
    assert requires_confirmation("edit_booking") is True
    assert requires_confirmation("cancel_booking") is True
    assert requires_confirmation("batch_move_bookings") is True

    assert requires_confirmation("check_availability") is False
    assert requires_confirmation("recommend_room") is False
    assert requires_confirmation("view_bookings") is False
def test_orchestrator_pauses_before_mutation():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)

        class MutationProvider(FakeProvider):
            def request_tool_call(self, user_message):
                return SimpleNamespace(
                    output_text=None,
                    steps=[
                        SimpleNamespace(
                            type="function_call",
                            name="book_room",
                            id="book_call",
                            arguments={
                                "room_id": 1,
                                "start_time": "2035-01-01T15:00:00Z",
                                "end_time": "2035-01-01T16:00:00Z",
                                "attendees": 4,
                            },
                        )
                    ],
                    id="interaction_book",
                )

        orchestrator.provider = MutationProvider()

        result = orchestrator.chat(
            user_message="Book room 1 tomorrow at 3 PM.",
            db=db,
        )

        assert "proceed" in result.lower()
        assert orchestrator.context.pending_action == "book_room"
        assert orchestrator.context.pending_arguments is not None

    finally:
        db.close()

def test_confirm_pending_action_executes_and_clears():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)

        orchestrator.context.set_pending_action(
            tool_name="book_room",
            arguments={
                "user_id": 1,
                "room_id": 1,
                "start_time": "2099-06-01T15:00:00Z",
                "end_time": "2099-06-01T16:00:00Z",
                "attendees": 4,
            },
        )

        result = orchestrator.confirm_pending_action(db)

        assert "completed successfully" in result
        assert orchestrator.context.pending_action is None
        assert orchestrator.context.pending_arguments is None
        assert orchestrator.context.last_booking_id is not None

        booking = db.get(
            __import__("api.models", fromlist=["Booking"]).Booking,
            orchestrator.context.last_booking_id,
        )

        assert booking is not None

        db.delete(booking)
        db.commit()

    finally:
        db.rollback()
        db.close()

def test_orchestrator_executes_pending_action_on_confirmation():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)

        orchestrator.context.set_pending_action(
            tool_name="book_room",
            arguments={
                "user_id": 1,
                "room_id": 1,
                "start_time": "2099-07-01T15:00:00Z",
                "end_time": "2099-07-01T16:00:00Z",
                "attendees": 4,
            },
        )

        result = orchestrator.chat(
            user_message="yes",
            db=db,
        )

        assert "completed successfully" in result
        assert orchestrator.context.pending_action is None
        assert orchestrator.context.last_booking_id is not None

        booking = db.get(
            Booking,
            orchestrator.context.last_booking_id,
        )

        assert booking is not None

        db.delete(booking)
        db.commit()

    finally:
        db.rollback()
        db.close()


def test_orchestrator_clears_pending_action_on_rejection():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)

        orchestrator.context.set_pending_action(
            tool_name="book_room",
            arguments={
                "user_id": 1,
                "room_id": 1,
                "start_time": "2035-04-01T15:00:00Z",
                "end_time": "2035-04-01T16:00:00Z",
                "attendees": 4,
            },
        )

        result = orchestrator.chat(
            user_message="no",
            db=db,
        )

        assert "cancelled" in result.lower()
        assert orchestrator.context.pending_action is None
        assert orchestrator.context.pending_arguments is None

    finally:
        db.close()
def test_orchestrator_keeps_pending_action_for_ambiguous_confirmation():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)

        arguments = {
            "user_id": 1,
            "room_id": 1,
            "start_time": "2035-05-01T15:00:00Z",
            "end_time": "2035-05-01T16:00:00Z",
            "attendees": 4,
        }

        orchestrator.context.set_pending_action(
            tool_name="book_room",
            arguments=arguments,
        )

        result = orchestrator.chat(
            user_message="What are you going to book?",
            db=db,
        )

        assert "confirmation" in result.lower()
        assert "yes" in result.lower()
        assert "no" in result.lower()

        assert orchestrator.context.pending_action == "book_room"
        assert orchestrator.context.pending_arguments == arguments

    finally:
        db.close()
def test_confirmation_and_rejection_messages_support_natural_language():
    assert is_confirmation_message("Yes, go ahead and book it.")
    assert is_confirmation_message("Yeah, book it.")
    assert is_confirmation_message("Sure, proceed.")
    assert is_confirmation_message("Okay, do it.")

    assert is_rejection_message("No, don't do that.")
    assert is_rejection_message("Nah, cancel it.")
    assert is_rejection_message("Never mind, don't book it.")
def test_confirmation_without_pending_action_goes_to_agent():
    db = SessionLocal()

    try:
        orchestrator = BoardBotOrchestrator(user_id=1)

        class ConfirmationProvider(FakeProvider):
            def request_tool_call(self, user_message):
                return SimpleNamespace(
                    output_text="There is no pending booking to confirm.",
                    steps=[],
                    id="interaction_confirmation",
                )

        orchestrator.provider = ConfirmationProvider()

        result = orchestrator.chat(
            user_message="Yes, go ahead.",
            db=db,
        )

        assert result == "There is no pending booking to confirm."
        assert orchestrator.context.pending_action is None

    finally:
        db.close()
def test_build_confirmation_message_for_booking():
    message = build_confirmation_message(
        tool_name="book_room",
        arguments={
            "room_id": 2,
            "start_time": "2090-06-01T15:00:00Z",
            "end_time": "2090-06-01T16:00:00Z",
            "attendees": 6,
        },
    )

    assert "room 2" in message
    assert "2090-06-01T15:00:00Z" in message
    assert "2090-06-01T16:00:00Z" in message
    assert "6 attendees" in message
    assert "proceed" in message.lower()
def test_build_confirmation_message_for_edit():
    message = build_confirmation_message(
        tool_name="edit_booking",
        arguments={
            "booking_id": 42,
            "room_id": 2,
            "start_time": "2095-08-01T15:00:00Z",
            "end_time": "2095-08-01T16:00:00Z",
            "attendees": 8,
        },
    )

    assert "booking 42" in message
    assert "room 2" in message
    assert "8 attendees" in message
    assert "proceed" in message.lower()
def test_build_confirmation_message_for_cancel():
    message = build_confirmation_message(
        tool_name="cancel_booking",
        arguments={
            "booking_id": 42,
        },
    )

    assert "cancel booking 42" in message.lower()
    assert "proceed" in message.lower()

def test_build_confirmation_message_for_batch_move():
    message = build_confirmation_message(
        tool_name="batch_move_bookings",
        arguments={
            "moves": [
                {
                    "booking_id": 41,
                    "room_id": 2,
                    "start_time": "2095-09-01T15:00:00Z",
                    "end_time": "2095-09-01T16:00:00Z",
                    "attendees": 5,
                },
                {
                    "booking_id": 42,
                    "room_id": 3,
                    "start_time": "2095-09-01T17:00:00Z",
                    "end_time": "2095-09-01T18:00:00Z",
                    "attendees": 8,
                },
            ],
        },
    )

    assert "2 bookings" in message
    assert "batch operation" in message
    assert "proceed" in message.lower()