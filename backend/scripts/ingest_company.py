import yaml
import json
from pathlib import Path
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Company, Asset, Document
from app.db.repositories import CompanyRepository, AssetRepository, DocumentRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


def load_company_spec(data_path: Path) -> Dict[str, Any]:
    spec_path = data_path / "specs" / "apexpetro_master.yaml"
    with open(spec_path) as f:
        return yaml.safe_load(f)


def load_document_registry(data_path: Path) -> Dict[str, Any]:
    registry_path = data_path / "metadata" / "document_registry.json"
    with open(registry_path) as f:
        return json.load(f)


def ingest_company(db: Session, data_path: Path) -> Dict[str, Any]:
    spec = load_company_spec(data_path)
    registry = load_document_registry(data_path)

    company_repo = CompanyRepository(db)
    asset_repo = AssetRepository(db)
    doc_repo = DocumentRepository(db)

    company_data = spec["company"]
    # Filter out fields not in model
    model_fields = {c.key for c in Company.__table__.columns}
    company_data_filtered = {k: v for k, v in company_data.items() if k in model_fields}
    company = company_repo.get_by_id(company_data_filtered["company_id"])
    if not company:
        company = company_repo.create(**company_data_filtered)
        logger.info("company_created", company_id=company.company_id)
    else:
        for k, v in company_data.items():
            setattr(company, k, v)
        db.commit()
        logger.info("company_updated", company_id=company.company_id)

    assets_data = spec.get("assets", [])
    for asset_data in assets_data:
        asset = asset_repo.get_by_id(asset_data["id"], company.company_id)
        if not asset:
            mapped_data = {
                "asset_id": asset_data["id"],
                "company_id": company.company_id,
                "asset_type": asset_data["type"],
                "unit": asset_data["unit"],
                "service": asset_data["service"],
                "criticality": asset_data["criticality"],
                "manufacturer": asset_data.get("manufacturer"),
                "model": asset_data.get("model"),
                "year": asset_data.get("year"),
                "design_pressure": asset_data.get("design_pressure"),
                "normal_pressure": asset_data.get("normal_pressure"),
                "design_temp": asset_data.get("design_temp"),
                "capacity": asset_data.get("capacity"),
            }
            asset_repo.create(**mapped_data)
        else:
            for k, v in asset_data.items():
                if k == "id":
                    setattr(asset, "asset_id", v)
                elif k == "type":
                    setattr(asset, "asset_type", v)
                elif hasattr(asset, k):
                    setattr(asset, k, v)
            db.commit()

    logger.info("assets_ingested", count=len(assets_data))

    doc_count = 0
    for doc_data in registry.get("documents", []):
        if "TEST_DATA_REMOVE_LATER" in doc_data.get("path", ""):
            continue

        doc = doc_repo.get_by_id(doc_data["document_id"], company.company_id)
        if not doc:
            full_path = data_path / doc_data["path"]
            if full_path.exists():
                import os
                file_size = full_path.stat().st_size
            else:
                file_size = 0

            doc = doc_repo.create(
                document_id=doc_data["document_id"],
                company_id=company.company_id,
                file_name=Path(doc_data["path"]).name,
                file_path=str(full_path),
                file_type=doc_data["type"].upper(),
                file_size=file_size,
                classification=doc_data["classification"],
                owner=doc_data.get("owner"),
                revision=doc_data.get("revision"),
                source_path=doc_data["path"],
            )
            doc_count += 1

    logger.info("documents_registered", count=doc_count)

    return {
        "company_id": company.company_id,
        "assets": len(assets_data),
        "documents": doc_count,
    }


def main():
    import sys
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("../ApexPetro_Sovereign_Dataset_v3")
    data_path = data_path.resolve()

    if not data_path.exists():
        logger.error("data_path_not_found", path=str(data_path))
        return 1

    db = SessionLocal()
    try:
        result = ingest_company(db, data_path)
        logger.info("ingestion_complete", **result)
        print(f"Success: {result}")
        return 0
    except Exception as e:
        logger.error("ingestion_failed", error=str(e))
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    from app.core.logging import configure_logging
    configure_logging()
    exit(main())