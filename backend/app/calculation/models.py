from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CalculationInput(BaseModel):
    value: Any
    unit: Optional[str] = None

    source: Optional[str] = None
    source_ref: Optional[str] = None

    timestamp: Optional[str] = None

    asset_id: Optional[str] = None
    dataset_ref: Optional[str] = None


class CalculationRequest(BaseModel):
    operation: str

    inputs: Dict[str, CalculationInput] = Field(
        default_factory=dict
    )

    dataset: Optional[List[Dict[str, Any]]] = None

    context: Dict[str, Any] = Field(
        default_factory=dict
    )


class CalculationResponse(BaseModel):
    calculation_id: str
    operation: str

    result: Any = None
    unit: Optional[str] = None

    formula: Optional[str] = None
    rule: Optional[Dict[str, Any]] = None

    status: str
    verification_status: str

    trace_id: str

    errors: List[str] = Field(
        default_factory=list
    )

    warnings: List[str] = Field(
        default_factory=list
    )