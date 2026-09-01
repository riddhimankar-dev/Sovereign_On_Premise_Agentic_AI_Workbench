from typing import Dict, Any, List
from app.tools.base import BaseTool, ToolInput, ToolOutput, tool_registry
from app.db.repositories import AssetRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class AssetLookupInput(ToolInput):
    asset_id: str = None
    query: str = None


class AssetLookupTool(BaseTool):
    name = "get_asset"
    description = "Look up asset information by ID or search assets by query"
    permission = "read"

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ToolOutput:
        db = context.get("db")
        company_id = context.get("company_id")

        if not db or not company_id:
            return ToolOutput(success=False, error="Missing db or company_id in context")

        asset_repo = AssetRepository(db)
        asset_id = input_data.get("asset_id")
        query = input_data.get("query")

        if asset_id:
            asset = asset_repo.get_by_id(asset_id, company_id)
            if asset:
                return ToolOutput(success=True, data={
                    "asset_id": asset.asset_id,
                    "asset_type": asset.asset_type,
                    "unit": asset.unit,
                    "service": asset.service,
                    "criticality": asset.criticality,
                    "manufacturer": asset.manufacturer,
                    "model": asset.model,
                    "year": asset.year,
                    "design_pressure": asset.design_pressure,
                    "normal_pressure": asset.normal_pressure,
                    "design_temp": asset.design_temp,
                    "capacity": asset.capacity,
                    "specifications": asset.specifications,
                })
            return ToolOutput(success=False, error=f"Asset {asset_id} not found")

        elif query:
            assets = asset_repo.search(company_id, query)
            return ToolOutput(success=True, data={
                "assets": [
                    {
                        "asset_id": a.asset_id,
                        "asset_type": a.asset_type,
                        "unit": a.unit,
                        "service": a.service,
                        "criticality": a.criticality,
                    }
                    for a in assets
                ]
            })

        return ToolOutput(success=False, error="Either asset_id or query required")


tool_registry.register(AssetLookupTool())