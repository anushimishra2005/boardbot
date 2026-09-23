from types import SimpleNamespace

from api.agent.orchestrator import BoardBotOrchestrator
from api.core.database import SessionLocal


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
                "start_time": "2035-01-01T15:00:00Z",
                "end_time": "2035-01-01T16:00:00Z",
            },
        )

        return SimpleNamespace(
            steps=[function_call],
            output_text=None,
            id="interaction_123",
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
                    "start_time": "2035-01-01T15:00:00Z",
                    "end_time": "2035-01-01T16:00:00Z",
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