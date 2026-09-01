from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Asset
from app.core.config import settings

router = APIRouter(prefix="/assets", tags=["assets"])


class AssetResponse(BaseModel):
    id: int
    asset_id: str
    asset_type: str
    unit: str
    service: str
    criticality: str
    manufacturer: str
    model: str
    year: int
    design_pressure: float
    normal_pressure: float
    design_temp: float
    capacity: str
    specifications: dict

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    assets: List[AssetResponse]
    total: int


@router.get("", response_model=AssetListResponse)
async def list_assets(
    company_id: Optional[str] = Query(None),
    unit: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Asset)
    if company_id:
        query = query.filter(Asset.company_id == company_id)
    else:
        query = query.filter(Asset.company_id == settings.company_id)
    if unit:
        query = query.filter(Asset.unit == unit)
    total = query.count()
    assets = query.order_by(Asset.asset_id).offset(offset).limit(limit).all()
    return AssetListResponse(
        assets=[AssetResponse.model_validate(asset) for asset in assets],
        total=total,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str, db: Session = Depends(get_db)):
    asset = db.query(Asset).filter(Asset.asset_id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetResponse.model_validate(asset)