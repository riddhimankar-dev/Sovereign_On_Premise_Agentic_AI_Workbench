import asyncio
import json
import sys
from datetime import datetime
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.database import SessionLocal
from app.agents.orchestrator import run_agent
from app.rag.retriever import HybridRetriever

configure_logging()
logger = get_logger(__name__)

TEST_QUERIES = [
    {
        "query": "What is P-102?",
        "expected_contains": ["P-102", "Centrifugal", "CDU-4", "Crude Transfer"],
        "category": "equipment"
    },
    {
        "query": "What is P-102's approved maximum operating pressure?",
        "expected_contains": ["40 bar"],
        "category": "equipment"
    },
    {
        "query": "What was P-102 pressure in 2024, 2025 and 2026?",
        "expected_contains": ["34", "37", "42"],
        "category": "historical"
    },
    {
        "query": "Is 42 bar within the approved operating limit?",
        "expected_contains": ["No", "40", "deviation", "2 bar"],
        "category": "reasoning"
    },
    {
        "query": "What is the difference between design pressure and operating maximum?",
        "expected_contains": ["50 bar", "40 bar", "design", "operating"],
        "category": "equipment"
    },
    {
        "query": "What conflict exists in the vendor report?",
        "expected_contains": ["45 bar", "vendor", "conflict", "40 bar"],
        "category": "cross-document"
    },
    {
        "query": "Does the dataset specify remaining service life for P-102?",
        "expected_contains": ["not specified", "not available", "Not specified"],
        "category": "hallucination"
    },
    {
        "query": "What is required for permit to work?",
        "expected_contains": ["permit", "work", "energy isolation", "HSE"],
        "category": "safety"
    },
]


async def test_retrieval():
    print("=" * 60)
    print("RETRIEVAL EVALUATION")
    print("=" * 60)

    db = SessionLocal()
    retriever = HybridRetriever(db)

    for test in TEST_QUERIES:
        query = test["query"]
        results = await retriever.retrieve(query, settings.company_id, limit=5)

        if results:
            top = results[0]
            print(f"✓ {query[:50]}... → {len(results)} results, top score: {top.get('score', 0):.3f}")
        else:
            print(f"✗ {query[:50]}... → NO RESULTS")

    db.close()


async def test_agent():
    print("\n" + "=" * 60)
    print("AGENT EVALUATION")
    print("=" * 60)

    db = SessionLocal()
    conversation_id = f"eval-{datetime.now().isoformat()}"

    for test in TEST_QUERIES:
        query = test["query"]
        print(f"\nQuery: {query}")

        try:
            answer_parts = []
            async for event in run_agent(db, settings.company_id, 1, query, conversation_id):
                if event.get("event") == "run_completed":
                    answer_parts.append(event.get("answer", ""))
                    break

            full_answer = " ".join(answer_parts)
            expected = test.get("expected_contains", [])
            found = all(e.lower() in full_answer.lower() for e in expected)

            status = "PASS" if found else "FAIL"
            print(f"  {status}: {full_answer[:200]}...")
            if not found:
                print(f"  Expected to contain: {expected}")

        except Exception as e:
            print(f"  ERROR: {e}")

    db.close()


async def main():
    print("SOVEREIGN AI WORKBENCH — EVALUATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Company: {settings.company_id}")

    await test_retrieval()
    await test_agent()

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())