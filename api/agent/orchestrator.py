import json

from sqlalchemy.orm import Session

from api.agent.dispatcher import dispatch_tool
from api.agent.gemini_provider import GeminiProvider

from api.agent.context import AgentContext

class BoardBotOrchestrator:
    """Coordinates Gemini reasoning and deterministic tool execution."""

    def __init__(self, user_id: int) -> None:
        self.provider = GeminiProvider()
        self.context = AgentContext(user_id)

    def chat(self, user_message: str, db: Session) -> str:
        """Process a user message and return BoardBot's final response."""

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

            interaction = self.provider.client.interactions.create(
                model=self.provider.model_name,
                previous_interaction_id=interaction.id,
                input=function_results,
                tools=self.provider.tools,
            )

        return "I couldn't complete the request after several tool steps."