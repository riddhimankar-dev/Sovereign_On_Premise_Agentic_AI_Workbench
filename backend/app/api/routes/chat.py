from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.db.models import User
from app.services.chat_service import ChatService
from app.core.config import settings
from app.core.logging import get_logger
import json
import uuid

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/attachments")
async def upload_chat_attachment(
    conversation_id: str = Form(...),
    file: UploadFile = File(...),
):
    from app.services.chat_attachment_service import save_chat_attachment
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    result = save_chat_attachment(conversation_id, file.filename or "file", content)
    return result


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

    chat_service = ChatService(db)
    final = {"answer": "", "evidence": [], "model": "", "run_id": ""}
    async for event in chat_service.process_chat(request.query, company_id, user_id, conversation_id):
        if event.get("event") == "run_completed":
            final["answer"] = event.get("answer", "")
            final["evidence"] = event.get("evidence", [])
            final["model"] = event.get("model", "")
            final["run_id"] = event.get("run_id", "")

    return ChatResponse(
        conversation_id=conversation_id,
        run_id=final["run_id"],
        answer=final["answer"],
        evidence=final["evidence"],
        model=final["model"],
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
                "sources": m.sources or [],
                "artifacts": m.artifacts or [],
                "meta": m.meta or {},
                "attachments": m.attachments or [],
                "created_at": str(m.created_at),
            }
            for m in messages
        ],
        "total": len(messages),
    }


class RenameConversationRequest(BaseModel):
    title: str


@router.patch("/conversations/{conversation_id}")
async def rename_conversation(conversation_id: str, request: RenameConversationRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.db.repositories import ConversationRepository
    repo = ConversationRepository(db)
    title = (request.title or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    conv = repo.rename(conversation_id, title)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "conversation_id": conv.conversation_id,
        "title": conv.title,
        "created_at": str(conv.created_at),
        "updated_at": str(conv.updated_at),
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.db.repositories import ConversationRepository
    from app.services.chat_attachment_service import clear_conversation_attachments
    repo = ConversationRepository(db)
    existed = repo.delete(conversation_id)
    try:
        clear_conversation_attachments(conversation_id)
    except Exception:
        pass
    if not existed:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"conversation_id": conversation_id, "deleted": True}


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    from app.db.models import AgentRun
    runs = db.query(AgentRun).filter(
        AgentRun.conversation_id == conversation_id
    ).order_by(AgentRun.started_at.desc()).all()

    return {"conversation_id": conversation_id, "runs": [r.run_id for r in runs]}