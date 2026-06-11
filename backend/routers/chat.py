from fastapi import APIRouter, Depends

from ..agents import orchestrator
from ..core.config import UserContext, get_user_context
from ..models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest,
               ctx: UserContext = Depends(get_user_context)) -> ChatResponse:
    return await orchestrator.handle(ctx, req)
