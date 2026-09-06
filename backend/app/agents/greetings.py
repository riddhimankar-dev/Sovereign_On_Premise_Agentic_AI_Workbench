import re
from typing import Any, Dict, Optional
from app.llm.ollama_client import ollama_client
from app.llm.router import model_router
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Expressions that indicate a purely social/greeting intent with no subject
# requiring RAG or tool execution. Anything that also names an asset, document,
# operational metric, or a task-like verb is NOT routed to the fast path.
GREETING_PATTERNS = [
    r"\b(hi|hello|hey|good\s*(morning|afternoon|evening)|greetings|howdy|yo|hii+|helloo+)\b",
    r"(thanks|thank\s*you|thankyou|thx|ty)",
    r"\b(how\s*are\s*you|how's\s*it\s*going|how\s*r\s*u|hows\s*it)\b",
    r"\b(have\s*a\s*great\s*day|have\s*a\s*good\s*one|goodbye|bye|see\s*ya|see\s*you)\b",
    r"\byou\s*(are|'re)\s*(awesome|great|the\s*best|helpful)\b",
    r"\b(who\s*are\s*you|what\s*can\s*you\s*do|what\s*are\s*you|your\s*name)\b",
    r"^\s*(ok|okay|alright|sure|great|nice|cool|good)\s*[.!]?\s*$",
]

# If the query mentions any of these, it is a real question, not a greeting.
SUBJECT_HINTS = [
    "pressure", "corrosion", "vibration", "inspection", "p-102", "pump",
    "asset", "flow rate", "temperature", "report", "create", "generate",
    "analy", "document", "sop", "manual", "maximum", "minimum", "limit",
    "deviation", "work order", "risk", "what is", "how to", "why",
]


def is_greeting(query: str) -> bool:
    q = query.strip().lower()
    if not q:
        return False
    if any(hint in q for hint in SUBJECT_HINTS):
        return False
    return any(re.search(p, q) for p in GREETING_PATTERNS)


async def greet(query: str) -> Optional[Dict[str, Any]]:
    if not is_greeting(query):
        return None

    try:
        model = model_router.pick("general")
        response = await ollama_client.generate(
            model=model,
            prompt=f"User said: {query}",
            system=(
                "You are a friendly industrial AI assistant for ApexPetro Energy Limited. "
                "Respond briefly and warmly to the greeting or chitchat. "
                "Mention gently that you can help with engineering documents, inspections, "
                "pressure/corrosion analysis, approvals, and report generation. Keep it to 1-3 sentences."
            ),
            options={"temperature": 0.4},
        )
        return {"reply": response.get("response", "").strip(), "model": model}
    except Exception as e:
        logger.warning("greeting_generation_failed", error=str(e))
        return {"reply": "Hello! I'm the ApexPetro workbench assistant. I can help with your engineering documents, inspections, analyses, and approvals.", "model": "fallback"}


def fast_path_response(query: str) -> Optional[Dict[str, Any]]:
    q = query.strip().lower()
    if q in {"hi", "hello", "hey", "yo", "hi there", "hello there"}:
        return {
            "reply": "Hello! I'm your ApexPetro workbench assistant. Ask me about a document, an inspection, an analysis, or to create an approval/report.",
            "model": "fast-path",
        }
    return None