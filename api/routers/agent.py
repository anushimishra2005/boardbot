from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.agent.orchestrator import BoardBotOrchestrator
from api.core.dependencies import get_current_user, get_db
from api.models.user import User


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


class AgentChatRequest(BaseModel):
    message: str


class AgentChatResponse(BaseModel):
    response: str


@router.post(
    "/chat",
    response_model=AgentChatResponse,
)
def chat_with_agent(
    request: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orchestrator = BoardBotOrchestrator(
        user_id=current_user.id,
    )

    response = orchestrator.chat(
        user_message=request.message,
        db=db,
    )

    return AgentChatResponse(
        response=response,
    )