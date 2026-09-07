from typing import Any, Dict, List, Optional
import os
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import CalculationRecord

from app.calculation.engine import CalculationEngine
from app.calculation.models import CalculationRequest
from app.calculation.units import convert
from app.calculation.spreadsheet import spreadsheet_to_dataset


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/calculations",
    tags=["Calculations"],
)

engine = CalculationEngine()

# In-memory cache backed by persistent database records.
_calculation_store: Dict[str, Dict[str, Any]] = {}


# ============================================================
# MULTI-PARAMETER REQUEST MODELS
# ============================================================

class MultiParameter(BaseModel):
    name: str
    actual: float
    limit: float
    unit: Optional[str] = None
    source: Optional[str] = None
    source_ref: Optional[str] = None
    thresholds: Optional[Dict[str, float]] = None


class MultiParameterRequest(BaseModel):
    parameters: List[MultiParameter] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)


# ============================================================
# SAVE CALCULATION RESULT
# ============================================================

def _save_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save a calculation result in both:
    1. In-memory cache
    2. Persistent CalculationRecord database table
    """

    calculation_id = result.get("calculation_id")

    if not calculation_id:
        return result

    # --------------------------------------------------------
    # In-memory storage
    # --------------------------------------------------------

    _calculation_store[calculation_id] = result

    # --------------------------------------------------------
    # Persistent database storage
    # --------------------------------------------------------

    db = SessionLocal()

    try:
        record = (
            db.query(CalculationRecord)
            .filter(
                CalculationRecord.calculation_id == calculation_id
            )
            .first()
        )

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
            "verification_status": result.get(
                "verification_status",
                "PENDING",
            ),
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


# ============================================================
# LIST CALCULATIONS
# ============================================================

@router.get("")
async def list_calculations(limit: int = 50):
    """
    List persistent calculation summaries
    for the current company.
    """

    limit = max(1, min(limit, 200))

    db = SessionLocal()

    try:
        records = (
            db.query(CalculationRecord)
            .filter(
                CalculationRecord.company_id
                == settings.company_id
            )
            .order_by(
                CalculationRecord.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return {
            "calculations": [
                {
                    "calculation_id": record.calculation_id,
                    "trace_id": record.trace_id,
                    "operation": record.operation,
                    "result": record.result,
                    "unit": record.unit,
                    "status": record.status,
                    "verification_status": (
                        record.verification_status
                    ),
                    "created_at": (
                        record.created_at.isoformat()
                        if record.created_at
                        else None
                    ),
                }
                for record in records
            ],
            "total": len(records),
        }

    finally:
        db.close()


# ============================================================
# EXECUTE GENERAL CALCULATION
# ============================================================

@router.post("/execute")
async def execute_calculation(
    request: CalculationRequest,
):
    """
    Execute a deterministic Calculation Engine operation.

    Supports:
    - arithmetic
    - ratio
    - percentage deviation
    - percentage change
    - statistics
    - trend
    - moving average
    - petroleum calculations
    - equipment calculations
    - multi-parameter analysis
    """

    try:

        result = engine.execute(
            operation=request.operation,

            inputs={
                key: value.model_dump()
                for key, value in request.inputs.items()
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
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": request.operation,
                "error_type": "CALCULATION_ENGINE_ERROR",
            },
        )


# ============================================================
# SPREADSHEET → CALCULATION ENGINE
# ============================================================

@router.post("/spreadsheet")
async def spreadsheet_calculation(
    file: UploadFile = File(...),
    operation: str = Form(...),
    value_column: str = Form("value"),
    unit_column: str = Form("unit"),
    period_column: str = Form("period"),
    sheet_name: str = Form(""),
):
    """
    Upload a CSV/XLSX/XLSM file and perform a deterministic
    Calculation Engine operation on the spreadsheet data.

    Supported operations:
    - statistics
    - mean
    - median
    - trend
    - moving_average

    The uploaded file is stored temporarily and removed
    immediately after calculation.
    """

    filename = file.filename or ""

    extension = os.path.splitext(filename)[1].lower()

    # --------------------------------------------------------
    # Validate file format
    # --------------------------------------------------------

    allowed_extensions = {
        ".csv",
        ".xlsx",
        ".xlsm",
    }

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported spreadsheet format.",
                "supported_formats": [
                    ".csv",
                    ".xlsx",
                    ".xlsm",
                ],
            },
        )

    # --------------------------------------------------------
    # Validate calculation operation
    # --------------------------------------------------------

    allowed_operations = {
        "statistics",
        "mean",
        "median",
        "trend",
        "moving_average",
    }

    if operation not in allowed_operations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": (
                    f"Spreadsheet operation "
                    f"'{operation}' is not allowed."
                ),
                "allowed_operations": sorted(
                    allowed_operations
                ),
            },
        )

    temp_path: Optional[str] = None

    try:

        # ----------------------------------------------------
        # Read uploaded file
        # ----------------------------------------------------

        content = await file.read()

        # 10 MB safety limit
        max_size = 10 * 1024 * 1024

        if len(content) > max_size:
            raise HTTPException(
                status_code=413,
                detail=(
                    "Spreadsheet exceeds the "
                    "10 MB calculation limit."
                ),
            )

        # ----------------------------------------------------
        # Create controlled temporary file
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:

            temp_path = temp_file.name
            temp_file.write(content)

        # ----------------------------------------------------
        # Parse spreadsheet
        # ----------------------------------------------------

        dataset_result = spreadsheet_to_dataset(
            file_path=temp_path,
            value_column=value_column or None,
            unit_column=unit_column or None,
            period_column=period_column or None,
            sheet_name=sheet_name or None,
        )

        dataset = dataset_result.get(
            "dataset",
            [],
        )

        if not dataset:
            raise ValueError(
                "Spreadsheet contains no usable data."
            )

        # ----------------------------------------------------
        # Fix provenance
        #
        # spreadsheet_to_dataset uses the temporary path as
        # source_ref. Replace that with the actual uploaded
        # filename so sensitive local filesystem paths are
        # never exposed in calculation traces.
        # ----------------------------------------------------

        cleaned_dataset = []

        for row in dataset:

            item = dict(row)

            item["source_ref"] = filename

            cleaned_dataset.append(item)

        # ----------------------------------------------------
        # Execute deterministic calculation
        # ----------------------------------------------------

        result = engine.execute(
            operation=operation,

            inputs={},

            dataset=cleaned_dataset,

            context={
                "source_file": filename,
                "source_type": dataset_result.get(
                    "source_type"
                ),
                "sheet": dataset_result.get(
                    "sheet"
                ),
                "spreadsheet_calculation": True,
            },
        )

        # ----------------------------------------------------
        # Add spreadsheet provenance
        # ----------------------------------------------------

        result["spreadsheet"] = {
            "filename": filename,

            "source_type": dataset_result.get(
                "source_type"
            ),

            "sheet": dataset_result.get(
                "sheet"
            ),

            "columns": dataset_result.get(
                "columns",
                [],
            ),

            "row_count": dataset_result.get(
                "row_count",
                len(cleaned_dataset),
            ),

            "value_column": value_column,

            "unit_column": unit_column,

            "period_column": period_column,

            "engine_version": dataset_result.get(
                "engine_version"
            ),
        }

        # ----------------------------------------------------
        # Save calculation
        # ----------------------------------------------------

        return _save_result(result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "operation": operation,
                "error_type": (
                    "SPREADSHEET_CALCULATION_ERROR"
                ),
                "source_file": filename,
            },
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": operation,
                "error_type": (
                    "SPREADSHEET_CALCULATION_ENGINE_ERROR"
                ),
                "source_file": filename,
            },
        )

    finally:

        # ----------------------------------------------------
        # Always delete temporary uploaded file
        # ----------------------------------------------------

        if temp_path and os.path.exists(temp_path):

            try:
                os.remove(temp_path)
            except OSError:
                pass


# ============================================================
# STATISTICS
# ============================================================

@router.post("/statistics")
async def statistics(
    request: CalculationRequest,
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
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": "statistics",
                "error_type": "CALCULATION_ENGINE_ERROR",
            },
        )


# ============================================================
# TREND
# ============================================================

@router.post("/trend")
async def trend(
    request: CalculationRequest,
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
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": "trend",
                "error_type": "CALCULATION_ENGINE_ERROR",
            },
        )


# ============================================================
# MEAN
# ============================================================

@router.post("/mean")
async def mean(
    request: CalculationRequest,
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
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": "mean",
                "error_type": "CALCULATION_ENGINE_ERROR",
            },
        )


# ============================================================
# MEDIAN
# ============================================================

@router.post("/median")
async def median(
    request: CalculationRequest,
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
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": "median",
                "error_type": "CALCULATION_ENGINE_ERROR",
            },
        )


# ============================================================
# MOVING AVERAGE
# ============================================================

@router.post("/moving-average")
async def moving_average(
    request: CalculationRequest,
):

    try:

        result = engine.execute(
            operation="moving_average",

            inputs={
                key: value.model_dump()
                for key, value in request.inputs.items()
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
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": "moving_average",
                "error_type": "CALCULATION_ENGINE_ERROR",
            },
        )


# ============================================================
# MULTI-PARAMETER ANALYSIS
# ============================================================

@router.post("/multi-parameter")
async def multi_parameter_analysis(
    request: MultiParameterRequest,
):
    """
    Analyze multiple engineering parameters independently.

    Example:

    Pressure:
        actual = 42 bar
        limit = 40 bar

    Temperature:
        actual = 78 C
        limit = 80 C

    Vibration:
        actual = 4.2 mm/s
        limit = 4.5 mm/s
    """

    try:

        if not request.parameters:

            raise ValueError(
                "At least one engineering parameter "
                "is required."
            )

        inputs = {
            "parameters": [
                parameter.model_dump()
                for parameter in request.parameters
            ]
        }

        result = engine.execute(
            operation="multi_parameter_analysis",

            inputs=inputs,

            dataset=None,

            context=request.context,
        )

        return _save_result(result)

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": str(exc),
                "operation": (
                    "multi_parameter_analysis"
                ),
                "error_type": "VALIDATION_ERROR",
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": (
                    "multi_parameter_analysis"
                ),
                "error_type": (
                    "CALCULATION_ENGINE_ERROR"
                ),
            },
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
    """
    Deterministic engineering unit conversion.
    """

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
                "error_type": (
                    "UNIT_CONVERSION_ERROR"
                ),
            },
        )


# ============================================================
# THRESHOLD / RULE EVALUATION
# ============================================================

@router.post("/threshold")
async def threshold(
    request: CalculationRequest,
):
    """
    Evaluate an actual value against a reference/limit.

    Current implementation uses the deterministic
    percentage-deviation calculation and the registered
    engineering rule associated with the context.
    """

    try:

        if "actual" not in request.inputs:

            raise ValueError(
                "Input 'actual' is required."
            )

        if "reference" not in request.inputs:

            raise ValueError(
                "Input 'reference' is required."
            )

        result = engine.execute(
            operation="percentage_deviation",

            inputs={
                key: value.model_dump()
                for key, value in request.inputs.items()
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
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": str(exc),
                "operation": "threshold",
                "error_type": "CALCULATION_ENGINE_ERROR",
            },
        )


# ============================================================
# GET CALCULATION RESULT
# ============================================================

@router.get("/{calculation_id}")
async def get_calculation(
    calculation_id: str,
):
    """
    Retrieve a calculation result by calculation ID.
    """

    result = _calculation_store.get(
        calculation_id
    )

    # --------------------------------------------------------
    # Fallback to database
    # --------------------------------------------------------

    if not result:

        db = SessionLocal()

        try:

            record = (
                db.query(CalculationRecord)
                .filter(
                    CalculationRecord.calculation_id
                    == calculation_id,
                    CalculationRecord.company_id
                    == settings.company_id,
                )
                .first()
            )

            if record:

                result = {
                    "calculation_id": (
                        record.calculation_id
                    ),

                    "trace_id": record.trace_id,

                    "operation": record.operation,

                    "result": record.result,

                    "unit": record.unit,

                    "formula": record.formula,

                    "rule": record.rule,

                    "status": record.status,

                    "verification_status": (
                        record.verification_status
                    ),

                    "trace": record.trace,
                }

        finally:
            db.close()

    if not result:

        raise HTTPException(
            status_code=404,
            detail={
                "error": "Calculation not found.",
                "calculation_id": calculation_id,
            },
        )

    return result


# ============================================================
# GET CALCULATION TRACE
# ============================================================

@router.get("/{calculation_id}/trace")
async def get_calculation_trace(
    calculation_id: str,
):
    """
    Retrieve the complete deterministic calculation trace.
    """

    result = _calculation_store.get(
        calculation_id
    )

    # --------------------------------------------------------
    # Fallback to database
    # --------------------------------------------------------

    if not result:

        db = SessionLocal()

        try:

            record = (
                db.query(CalculationRecord)
                .filter(
                    CalculationRecord.calculation_id
                    == calculation_id,
                    CalculationRecord.company_id
                    == settings.company_id,
                )
                .first()
            )

            if record:

                result = {
                    "trace": record.trace
                }

        finally:
            db.close()

    if not result:

        raise HTTPException(
            status_code=404,
            detail={
                "error": (
                    "Calculation trace not found."
                ),
                "calculation_id": calculation_id,
            },
        )

    trace = result.get("trace")

    if trace is None:

        raise HTTPException(
            status_code=404,
            detail={
                "error": (
                    "Trace is not available."
                ),
                "calculation_id": calculation_id,
            },
        )

    return trace