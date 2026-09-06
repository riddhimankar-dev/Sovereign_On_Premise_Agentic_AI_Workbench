"""Deterministic conversation title generation.

Derives a short, readable chat title from the user's first message without
requiring an LLM call (fast, offline, and unit-testable). Falls back to a
cleaned prefix of the original query when no meaningful focus is found.
"""

import re
from typing import List, Optional

# Phrases a user typically opens with that carry no meaning for a title.
PREFIX_PHRASES: List[str] = [
    "can you please",
    "could you please",
    "i would like you to",
    "i'd like you to",
    "i want you to",
    "i need you to",
    "can i get",
    "could you",
    "would you",
    "can you",
    "do you know",
    "do you have",
    "i would like to",
    "i'd like to",
    "i want to",
    "i need to",
    "please help me",
    "help me",
    "kindly",
    "please",
    "hey",
    "hi",
    "hello",
]

# Leading action words that should be dropped when they introduce the query.
ACTION_PREFIXES: List[str] = [
    "explain how",
    "explain why",
    "explain what",
    "explain",
    "describe",
    "tell me about",
    "tell me",
    "show me",
    "give me",
    "summarize",
    "summarise",
    "what is",
    "what are",
    "what's",
    "whats",
    "how does",
    "how do",
    "how can",
    "how is",
    "how are",
    "why is",
    "why does",
    "who is",
    "when does",
    "where is",
    "where can",
    "which is",
    "create an",
    "create the",
    "create a",
    "create",
    "generate an",
    "generate the",
    "generate a",
    "generate",
    "make an",
    "make the",
    "make a",
    "make me",
    "make",
    "write an",
    "write the",
    "write a",
    "write",
    "build an",
    "build the",
    "build a",
    "build",
    "draft an",
    "draft the",
    "draft a",
    "draft",
    "prepare an",
    "prepare the",
    "prepare a",
    "prepare",
    "produce",
    "look up",
    "find",
    "check",
    "compare",
    "calculate",
    "analyze",
    "analyse",
    "review",
    "list",
]

LEADING_DROP_WORDS: set = {"the", "a", "an", "our", "your", "my"}

# Document-type words whose presence turns a query into a title like
# "<Focus> <Doc Type>" instead of "<Doc Type> <focus>".
DOC_TYPE_WORDS: List[str] = [
    "inspection report",
    "risk assessment",
    "approval note",
    "executive summary",
    "management summary",
    "impact assessment",
    "incident report",
    "maintenance report",
    "technical review",
    "compliance report",
    "audit report",
    "safety analysis",
    "performance report",
    "project plan",
    "assessment",
    "document",
    "analysis",
    "summary",
    "report",
]

# Words that add noise at the end of a title.
TRAILING_NOISE: set = {
    "please", "help", "me", "work", "works", "working", "know", "tell",
    "explain", "describe", "is", "are", "was", "were", "be", "the", "a",
    "an", "and", "or", "to", "for", "about", "on", "with", "in", "at", "of",
    "please", "thanks", "thank", "you", "does", "do", "did", "how", "why",
    "what", "when", "where", "can", "could", "would", "should", "i", "we",
}

CONNECTOR_WORDS: set = {
    "the", "a", "an", "of", "on", "for", "with", "in", "to", "at", "and",
    "or", "by", "from",
}


def _normalize(query: str) -> str:
    text = query.strip().lower()
    text = text.replace("'s", " ").replace("’s", " ")
    text = re.sub(r"[^a-z0-9&%.\-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _strip_prefixes(words: List[str]) -> List[str]:
    """Repeatedly drop leading politeness/action phrases and articles."""
    text = " ".join(words)
    changed = True
    while changed:
        changed = False
        lowered = text
        for phrase in PREFIX_PHRASES + ACTION_PREFIXES:
            if lowered.startswith(phrase):
                rest = lowered[len(phrase):].strip()
                if rest:
                    text = rest
                    changed = True
                    break
        lowered = text.lstrip()
        # leading articles / possessive subjects
        rest = lowered.split(" ")
        while rest and rest[0] in LEADING_DROP_WORDS:
            rest.pop(0)
        new_text = " ".join(rest)
        if new_text != text:
            text = new_text
            changed = True
    return text.split()


def _drop_trailing_noise(words: List[str]) -> List[str]:
    while words and words[-1] in TRAILING_NOISE:
        words.pop()
    return words


def _find_doc_type(words: List[str]) -> Optional[tuple]:
    """Return (focus_words, doc_type_words) if the phrase is '<doc type> on/for/about <focus>'."""
    joined = " ".join(words)
    for dt in sorted(DOC_TYPE_WORDS, key=len, reverse=True):
        m = re.match(rf"^({re.escape(dt)})\s+(?:on|about|for|of|regarding|covering|relating|to)\s+(.+)$", joined)
        if m:
            doc_type = dt
            focus = m.group(2).strip()
            return focus.split(), doc_type.split()
    return None


def _title_case(words: List[str]) -> str:
    cleaned = []
    for i, w in enumerate(words):
        if w.lower() in CONNECTOR_WORDS and i != 0:
            cleaned.append(w.lower())
        elif re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", w) and not any(ch.isdigit() for ch in w) and len(w) > 1:
            cleaned.append(w.capitalize())
        elif any(ch.isdigit() for ch in w) and re.fullmatch(r"[a-z0-9.\-]+", w):
            cleaned.append(w.upper())
        else:
            cleaned.append(w.upper() if w.isupper() else w.capitalize())
    return " ".join(cleaned)


def generate_title(query: str, max_words: int = 6) -> str:
    original = query.strip()
    if not original:
        return ""
    normalized = _normalize(original)
    words = normalized.split()
    if not words:
        return original[:60]

    words = _strip_prefixes(words)
    words = _drop_trailing_noise(list(words))

    doc_pair = _find_doc_type(words)
    if doc_pair:
        focus, doc_type = doc_pair
        focus = _drop_trailing_noise(list(focus))
        combined = (focus + doc_type) if focus else doc_type
    else:
        combined = words

    combined = [w for w in combined if w]
    combined = _drop_trailing_noise(list(combined))
    while combined and combined[0] in LEADING_DROP_WORDS and len(combined) > 1:
        combined.pop(0)
    combined = combined[:max_words]
    title = _title_case(combined).strip()

    if not title:
        fallback = normalized.split()[:max_words]
        title = _title_case(fallback)

    if not title:
        title = original[:60]
    return title.rstrip(".,;:").strip()[:80] or original[:60].strip()