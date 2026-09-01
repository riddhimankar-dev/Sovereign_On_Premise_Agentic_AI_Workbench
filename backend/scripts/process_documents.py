import asyncio
from app.db.database import SessionLocal
from app.services.document_service import ingest_all_documents
from app.core.config import settings

async def main():
    db = SessionLocal()
    try:
        result = await ingest_all_documents(db, settings.company_id)
        print(f"Processed: {result}")
    finally:
        db.close()

if __name__ == "__main__":
    from app.core.logging import configure_logging
    configure_logging()
    asyncio.run(main())
