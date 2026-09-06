from datetime import datetime, timezone
import uuid


ENGINE_VERSION = "1.0.0"


def create_trace(
    operation,
    inputs,
    formula,
    result,
    unit,
    rule=None,
    verification_status="PENDING",
):

    calculation_id = (
        f"CAL-{uuid.uuid4().hex[:12].upper()}"
    )

    trace_id = (
        f"TRACE-{uuid.uuid4().hex[:12].upper()}"
    )

    return {
        "calculation_id": calculation_id,
        "trace_id": trace_id,

        "operation": operation,

        "inputs": inputs,

        "formula": formula,

        "rule": rule,

        "result": result,
        "unit": unit,

        "engine_version": ENGINE_VERSION,

        "formula_version": "1.0",

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "verification_status": verification_status,
    }