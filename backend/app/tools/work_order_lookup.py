from typing import Dict, Any
from app.tools.base import BaseTool, ToolInput, ToolOutput, tool_registry
from app.db.repositories import WorkOrderRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class WorkOrderLookupInput(ToolInput):
    asset_id: str = None
    wo_id: str = None
    status: str = None


class WorkOrderLookupTool(BaseTool):
    name = "get_work_orders"
    description = "Look up work orders by asset ID, work order ID, or status"
    permission = "read"

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ToolOutput:
        db = context.get("db")
        company_id = context.get("company_id")

        if not db or not company_id:
            return ToolOutput(success=False, error="Missing db or company_id in context")

        wo_repo = WorkOrderRepository(db)

        asset_id = input_data.get("asset_id")
        wo_id = input_data.get("wo_id")
        status = input_data.get("status")

        if wo_id:
            from app.db.models import WorkOrder
            wo = db.query(WorkOrder).filter(
                WorkOrder.wo_id == wo_id,
                WorkOrder.company_id == company_id
            ).first()
            if wo:
                return ToolOutput(success=True, data={
                    "wo_id": wo.wo_id,
                    "asset_id": wo.asset_id,
                    "title": wo.title,
                    "description": wo.description,
                    "status": wo.status.value,
                    "priority": wo.priority,
                })
            return ToolOutput(success=False, error=f"Work order {wo_id} not found")

        elif asset_id:
            work_orders = wo_repo.list_by_asset(asset_id, company_id)
            if status:
                work_orders = [wo for wo in work_orders if wo.status.value == status]
            return ToolOutput(success=True, data={
                "work_orders": [
                    {
                        "wo_id": wo.wo_id,
                        "asset_id": wo.asset_id,
                        "title": wo.title,
                        "status": wo.status.value,
                        "priority": wo.priority,
                    }
                    for wo in work_orders
                ]
            })

        return ToolOutput(success=False, error="Either wo_id or asset_id required")


tool_registry.register(WorkOrderLookupTool())