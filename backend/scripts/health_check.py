import asyncio
import httpx
import sys
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.db.database import SessionLocal
from app.db.models import Company, Asset, Document, ModelRegistry
from sqlalchemy import text

configure_logging()
logger = get_logger(__name__)


async def check_database() -> bool:
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error("db_check_failed", error=str(e))
        return False


async def check_ollama() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                available = {m["name"] for m in models}
                required = {settings.primary_model, settings.coding_model, settings.router_model, settings.embedding_model}
                return required.issubset(available)
    except Exception as e:
        logger.error("ollama_check_failed", error=str(e))
    return False


async def check_qdrant() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.qdrant_url}/health")
            return resp.status_code == 200
    except Exception as e:
        logger.error("qdrant_check_failed", error=str(e))
    return False


async def check_company_data() -> bool:
    try:
        db = SessionLocal()
        company = db.query(Company).filter(Company.company_id == settings.company_id).first()
        if not company:
            return False
        assets = db.query(Asset).filter(Asset.company_id == settings.company_id).count()
        docs = db.query(Document).filter(Document.company_id == settings.company_id).count()
        models = db.query(ModelRegistry).count()
        db.close()
        logger.info("company_data_check", company=company.name, assets=assets, documents=docs, models=models)
        return assets > 0 and docs > 0
    except Exception as e:
        logger.error("company_data_check_failed", error=str(e))
    return False


async def main():
    print("=" * 50)
    print("SOVEREIGN AI WORKBENCH — HEALTH CHECK")
    print("=" * 50)

    checks = {
        "Database": await check_database(),
        "Ollama": await check_ollama(),
        "Qdrant": await check_qdrant(),
        "Company Data": await check_company_data(),
    }

    for name, passed in checks.items():
        status = "HEALTHY" if passed else "UNHEALTHY"
        print(f"  {status:10}  {name}")

    all_healthy = all(checks.values())
    print("=" * 50)
    if all_healthy:
        print("OVERALL: HEALTHY")
        return 0
    else:
        print("OVERALL: DEGRADED")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))