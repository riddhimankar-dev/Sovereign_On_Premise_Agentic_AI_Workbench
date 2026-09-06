from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import CalculationRecord

from app.calculation.engine import CalculationEngine
from app.calculation.models import CalculationRequest
from app.calculation.units import convert


router = APIRouter(
    prefix="/calculations",
    tags=["Calculations"]
)

engine = CalculationEngine()

# In-memory cache backed by persistent calculation records.
_calculation_store: Dict[str, Dict[str, Any]] = {}


def _save_result(result: Dict[str, Any]) -> Dict[str, Any]:
    calculation_id = result.get("calculation_id")

    if calculation_id:
        _calculation_store[calculation_id] = result
        db = SessionLocal()
        try:
            record = db.query(CalculationRecord).filter(
                CalculationRecord.calculation_id == calculation_id
            ).first()
            values = {
                "calculation_id": calculation_id,
                "trace_id": result.get("trace_id"),
                "company_id": settings.company_id,
                "operation": result.get("operation", "unknown"),
                "inputs": result.get("trace", {}).get("inputs", {}),
                "context": result.get("trace", {}).get("context", {}),
                "result": result.get("result"),
                "unit": result.get("unit"),
                "formula": result.get("formula"),
                "rule": result.get("rule"),
                "status": result.get("status", "NORMAL"),
                "verification_status": result.get("verification_status", "PENDING"),
                "trace": result.get("trace", {}),
            }
            if record:
                for key, value in values.items():
                    setattr(record, key, value)
            else:
                db.add(CalculationRecord(**values))
            db.commit()
        finally:
            db.close()

    return result


@router.get("")
async def list_calculations(limit: int = 50):
    """List persistent calculation summaries for the current company."""
    limit = max(1, min(limit, 200))
    db = SessionLocal()
    try:
        records = db.query(CalculationRecord).filter(
            CalculationRecord.company_id == settings.company_id
        ).order_by(CalculationRecord.created_at.desc()).limit(limit).all()
        return {
            "calculations": [
                {
                    "calculation_id": record.calculation_id,
                    "trace_id": record.trace_id,
                    "operation": record.operation,
                    "result": record.result,
                    "unit": record.unit,
                    "status": record.status,
                    "verification_status": record.verification_status,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                }
                for record in records
            ],
            "total": len(records),
        }
    finally:
        db.close()


# ============================================================
# EXECUTE
# ============================================================

@router.post("/execute")
async def execute_calculation(
    request: CalculationRequest
):

    try:

        result = engine.execute(
            operation=request.operation,

            inputs={
                key: value.model_dump()
                for key, value
                in request.inputs.items()
            },

            dataset=request.dataset,

            context=request.context,
        )

        return _save_result(result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "operation": request.operation,
                "error_type": "VALIDATION_ERROR",
            }
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": request.operation,
                "error_type": "CALCULATION_ENGINE_ERROR",
            }
        )


# ============================================================
# STATISTICS
# ============================================================

@router.post("/statistics")
async def statistics(
    request: CalculationRequest
):

    try:

        result = engine.execute(
            operation="statistics",

            inputs={},

            dataset=request.dataset,

            context=request.context,
        )

        return _save_result(result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "operation": "statistics",
                "error_type": "VALIDATION_ERROR",
            }
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": "statistics",
                "error_type": "CALCULATION_ENGINE_ERROR",
            }
        )


# ============================================================
# TREND
# ============================================================

@router.post("/trend")
async def trend(
    request: CalculationRequest
):

    try:

        result = engine.execute(
            operation="trend",

            inputs={},

            dataset=request.dataset,

            context=request.context,
        )

        return _save_result(result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "operation": "trend",
                "error_type": "VALIDATION_ERROR",
            }
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": "trend",
                "error_type": "CALCULATION_ENGINE_ERROR",
            }
        )


# ============================================================
# MEAN
# ============================================================

@router.post("/mean")
async def mean(
    request: CalculationRequest
):

    try:

        result = engine.execute(
            operation="mean",

            inputs={},

            dataset=request.dataset,

            context=request.context,
        )

        return _save_result(result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "operation": "mean",
                "error_type": "VALIDATION_ERROR",
            }
        )


# ============================================================
# MEDIAN
# ============================================================

@router.post("/median")
async def median(
    request: CalculationRequest
):

    try:

        result = engine.execute(
            operation="median",

            inputs={},

            dataset=request.dataset,

            context=request.context,
        )

        return _save_result(result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "operation": "median",
                "error_type": "VALIDATION_ERROR",
            }
        )


# ============================================================
# MOVING AVERAGE
# ============================================================

@router.post("/moving-average")
async def moving_average(
    request: CalculationRequest
):

    try:

        result = engine.execute(
            operation="moving_average",

            inputs={
                key: value.model_dump()
                for key, value
                in request.inputs.items()
            },

            dataset=request.dataset,

            context=request.context,
        )

        return _save_result(result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "operation": "moving_average",
                "error_type": "VALIDATION_ERROR",
            }
        )


# ============================================================
# UNIT CONVERSION
# ============================================================

@router.post("/unit-convert")
async def unit_convert(
    value: float,
    from_unit: str,
    to_unit: str,
):

    try:

        converted_value = convert(
            value,
            from_unit,
            to_unit,
        )

        return {
            "value": value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "converted_value": converted_value,
            "status": "VERIFIED",
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "error_type": "UNIT_CONVERSION_ERROR",
            }
        )


# ============================================================
# THRESHOLD / PRESSURE RULE
# ============================================================

@router.post("/threshold")
async def threshold(
    request: CalculationRequest
):

    try:

        # Threshold evaluation is currently handled through
        # percentage deviation for engineering parameters.

        if "actual" not in request.inputs:
            raise ValueError(
                "Input 'actual' is required"
            )

        if "reference" not in request.inputs:
            raise ValueError(
                "Input 'reference' is required"
            )

        result = engine.execute(
            operation="percentage_deviation",

            inputs={
                key: value.model_dump()
                for key, value
                in request.inputs.items()
            },

            dataset=request.dataset,

            context=request.context,
        )

        return _save_result(result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "operation": "threshold",
                "error_type": "VALIDATION_ERROR",
            }
        )


# ============================================================
# CALCULATION RESULT
# ============================================================

@router.get("/{calculation_id}")
async def get_calculation(
    calculation_id: str
):

    result = _calculation_store.get(calculation_id)
    if not result:
        db = SessionLocal()
        try:
            record = db.query(CalculationRecord).filter(
                CalculationRecord.calculation_id == calculation_id,
                CalculationRecord.company_id == settings.company_id,
            ).first()
            if record:
                result = {
                    "calculation_id": record.calculation_id,
                    "trace_id": record.trace_id,
                    "operation": record.operation,
                    "result": record.result,
                    "unit": record.unit,
                    "formula": record.formula,
                    "rule": record.rule,
                    "status": record.status,
                    "verification_status": record.verification_status,
                    "trace": record.trace,
                }
        finally:
            db.close()

    if not result:

        raise HTTPException(
            status_code=404,
            detail={
                "error": "Calculation not found",
                "calculation_id": calculation_id,
            }
        )

    return result


# ============================================================
# CALCULATION TRACE
# ============================================================

@router.get("/{calculation_id}/trace")
async def get_calculation_trace(
    calculation_id: str
):

    result = _calculation_store.get(calculation_id)
    if not result:
        db = SessionLocal()
        try:
            record = db.query(CalculationRecord).filter(
                CalculationRecord.calculation_id == calculation_id,
                CalculationRecord.company_id == settings.company_id,
            ).first()
            if record:
                result = {"trace": record.trace}
        finally:
            db.close()

    if not result:

        raise HTTPException(
            status_code=404,
            detail={
                "error": "Calculation trace not found",
                "calculation_id": calculation_id,
            }
        )

    trace = result.get(
        "trace"
    )

    if trace is None:

        raise HTTPException(
            status_code=404,
            detail={
                "error": "Trace is not available",
                "calculation_id": calculation_id,
            }
        )

    return trace