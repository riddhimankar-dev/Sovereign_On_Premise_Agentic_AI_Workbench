from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
from app.db.database import get_db
from app.services.chat_service import ChatService
from app.core.config import settings
from app.core.logging import get_logger
import json
import uuid

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    run_id: str
    answer: str
    evidence: list
    model: str


async def event_generator(
    query: str,
    company_id: str,
    user_id: int,
    conversation_id: str,
    db: Session,
) -> AsyncGenerator[str, None]:
    chat_service = ChatService(db)
    async for event in chat_service.process_chat(query, company_id, user_id, conversation_id):
        yield f"data: {json.dumps(event)}\n\n"


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    conversation_id = request.conversation_id or str(uuid.uuid4())
    company_id = settings.company_id
    user_id = 1

    async for event in run_agent(db, company_id, user_id, request.query, conversation_id):
        pass

    return ChatResponse(
        conversation_id=conversation_id,
        run_id="",
        answer="",
        evidence=[],
        model="",
    )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    conversation_id = request.conversation_id or str(uuid.uuid4())
    company_id = settings.company_id
    user_id = 1

    return StreamingResponse(
        event_generator(request.query, company_id, user_id, conversation_id, db),
        media_type="text/event-stream",
    )


@router.post("/conversations")
async def create_conversation(db: Session = Depends(get_db)):
    from app.db.repositories import ConversationRepository
    from app.core.config import settings
    conversation_id = str(uuid.uuid4())
    repo = ConversationRepository(db)
    conv = repo.get_or_create_by_conversation_id(conversation_id, settings.company_id, 1)
    return {
        "conversation_id": conv.conversation_id,
        "title": conv.title,
        "created_at": str(conv.created_at),
    }


@router.get("/conversations")
async def list_conversations(db: Session = Depends(get_db)):
    from app.db.repositories import ConversationRepository
    from app.core.config import settings
    repo = ConversationRepository(db)
    conversations = repo.list_by_user(settings.company_id, 1)
    return {
        "conversations": [
            {
                "conversation_id": c.conversation_id,
                "title": c.title,
                "created_at": str(c.created_at),
                "updated_at": str(c.updated_at),
            }
            for c in conversations
        ],
        "total": len(conversations),
    }


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: str, db: Session = Depends(get_db)):
    from app.db.repositories import ConversationRepository
    repo = ConversationRepository(db)
    messages = repo.get_messages(conversation_id)
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "message_id": m.message_id,
                "role": m.role,
                "content": m.content,
                "run_id": m.run_id,
                "created_at": str(m.created_at),
            }
            for m in messages
        ],
        "total": len(messages),
    }


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    from app.db.models import AgentRun
    runs = db.query(AgentRun).filter(
        AgentRun.conversation_id == conversation_id
    ).order_by(AgentRun.started_at.desc()).all()

    return {"conversation_id": conversation_id, "runs": [r.run_id for r in runs]}


from app.agents.orchestrator import run_agent