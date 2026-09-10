from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.cost_engine import CostEngine


router = APIRouter(
    prefix="/cost",
    tags=["Cost Intelligence"],
)


# ============================================================
# REQUEST MODELS
# ============================================================


class CostItem(BaseModel):
    """
    Engineering/BOM cost item.
    """

    name: str

    category: Optional[str] = None

    material: Optional[str] = None

    quantity: float = Field(
        gt=0
    )

    unit_cost: float = Field(
        ge=0
    )

    installation_cost: float = Field(
        default=0,
        ge=0
    )

    maintenance_cost: float = Field(
        default=0,
        ge=0
    )

    criticality: str = "low"

    safety_critical: bool = False


class CostEstimateRequest(BaseModel):
    """
    Request for cost estimation and budget analysis.
    """

    project_name: str

    budget: float = Field(
        gt=0
    )

    items: List[CostItem] = Field(
        min_length=1
    )


class WhatIfChange(BaseModel):
    """
    Modification to one item in a what-if scenario.
    """

    index: int = Field(
        ge=0
    )

    quantity: Optional[float] = Field(
        default=None,
        gt=0
    )

    unit_cost: Optional[float] = Field(
        default=None,
        ge=0
    )

    installation_cost: Optional[float] = Field(
        default=None,
        ge=0
    )

    maintenance_cost: Optional[float] = Field(
        default=None,
        ge=0
    )

    criticality: Optional[str] = None

    safety_critical: Optional[bool] = None

    name: Optional[str] = None

    category: Optional[str] = None

    material: Optional[str] = None


class WhatIfRequest(BaseModel):
    """
    Request for what-if cost analysis.
    """

    project_name: str

    budget: float = Field(
        gt=0
    )

    items: List[CostItem] = Field(
        min_length=1
    )

    changes: List[WhatIfChange] = Field(
        default_factory=list
    )

    scenario_budget: Optional[float] = Field(
        default=None,
        gt=0
    )


# ============================================================
# HELPER
# ============================================================


def _items_to_dict(
    items: List[CostItem],
) -> List[Dict[str, Any]]:
    """
    Convert Pydantic models to dictionaries
    accepted by CostEngine.
    """

    return [
        item.model_dump()
        for item in items
    ]


# ============================================================
# COST ESTIMATE
# ============================================================


@router.post("/estimate")
def estimate_cost(
    request: CostEstimateRequest,
):
    """
    Generate a deterministic engineering cost estimate.

    POST /api/cost/estimate
    """

    try:
        result = CostEngine.estimate(
            project_name=request.project_name,
            budget=request.budget,
            items=_items_to_dict(
                request.items
            ),
        )

        return {
            "status": "success",
            "operation": "cost_estimate",
            "result": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ============================================================
# BUDGET ANALYSIS
# ============================================================


@router.post("/budget-analysis")
def budget_analysis(
    request: CostEstimateRequest,
):
    """
    Analyze project cost against approved budget.

    POST /api/cost/budget-analysis
    """

    try:
        result = CostEngine.budget_analysis(
            project_name=request.project_name,
            budget=request.budget,
            items=_items_to_dict(
                request.items
            ),
        )

        return {
            "status": "success",
            "operation": "budget_analysis",
            "result": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ============================================================
# WHAT-IF ANALYSIS
# ============================================================


@router.post("/what-if")
def what_if_analysis(
    request: WhatIfRequest,
):
    """
    Compare baseline project cost with
    a modified what-if scenario.

    POST /api/cost/what-if
    """

    try:

        changes = {
            "items": [
                change.model_dump(
                    exclude_none=True
                )
                for change in request.changes
            ]
        }

        if request.scenario_budget is not None:
            changes["budget"] = (
                request.scenario_budget
            )

        result = CostEngine.what_if(
            project_name=request.project_name,
            budget=request.budget,
            items=_items_to_dict(
                request.items
            ),
            changes=changes,
        )

        return {
            "status": "success",
            "operation": "what_if",
            "result": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )