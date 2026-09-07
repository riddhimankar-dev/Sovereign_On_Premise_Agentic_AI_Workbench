from typing import Dict, Any, List, Optional
from app.agents.state import AgentState, AgentPlan, AgentStepModel, AgentPhase
from app.llm.ollama_client import ollama_client
from app.llm.router import model_router
from app.tools.base import tool_registry
from app.core.config import settings
from app.core.logging import get_logger
import json
import re

logger = get_logger(__name__)


# ============================================================
# PLANNING PROMPT
# ============================================================

PLANNING_PROMPT = """You are a planning agent for an industrial AI workbench.

Your task is to create a step-by-step execution plan for the user's query.

Available tools:
{tools}

IMPORTANT CALCULATION RULES:

1. Numerical calculations must use the controlled Calculation Engine.
2. Never use an LLM to perform engineering arithmetic when the
   Calculation Engine is available.
3. Never invent missing numerical values.
4. Never invent engineering limits or safety thresholds.
5. Numerical values should come from retrieved documents,
   OCR, spreadsheets, asset metadata, or approved configuration.
6. Every calculation input should preserve its unit and source.
7. If a required value is missing, retrieve it or clearly report
   that the value is unavailable.
8. The Calculation Engine is deterministic and authoritative
   for calculation results.
9. The LLM must not override a Calculation Engine result.
10. Historical trends must not automatically be treated as forecasts.

Petroleum calculation examples:

- "Calculate water cut for oil rate 800 BPD and water rate 200 BPD"
  -> call calculate with water_cut

- "Calculate total liquid rate for oil rate 800 BPD and water rate 200 BPD"
  -> call calculate with total_liquid_rate

- "Calculate GOR for gas rate 5000 SCF/day and oil rate 1000 BPD"
  -> call calculate with gas_oil_ratio

Equipment calculation examples:

- "Calculate pump efficiency"
  -> call calculate with pump_efficiency

- "Calculate MTBF"
  -> call calculate with mtbf

- "Calculate MTTR"
  -> call calculate with mttr

- "Calculate equipment availability"
  -> call calculate with equipment_availability

Other calculation examples:

- "Calculate how far P-102 is above its limit"
  -> retrieve actual pressure and approved pressure limit
  -> call calculate with absolute_deviation

- "What percentage above the limit is P-102?"
  -> retrieve actual pressure and approved limit
  -> call calculate with percentage_deviation

- "What is the percentage increase?"
  -> retrieve previous and current values
  -> call calculate with percentage_change

- "Calculate the average vibration"
  -> retrieve structured vibration dataset
  -> call calculate with statistics

- "Show the pressure trend"
  -> retrieve historical pressure series
  -> call calculate with trend

Guidelines:
1. Break down complex queries into logical steps.
2. Each step should use ONE tool.
3. Steps should build on each other.
4. Include retrieval, calculation, analysis, and reasoning as needed.
5. Calculations should use the controlled "calculate" tool.
6. End with verification and answer synthesis where appropriate.

Respond with ONLY a JSON object:
{
  "steps": [
    {
      "label": "Step description",
      "tool": "tool_name",
      "input": {...}
    }
  ]
}
"""


class Planner:

    # ========================================================
    # EXISTING ANALYSIS KEYWORDS
    # ========================================================

    ANALYSIS_KEYWORDS = [
        "analyz",
        "analyse",
        "trend",
        "compare",
        "average",
        "summary of",
        "overview",
        "dashboard",
        "metrics",
        "kpi",
        "risk assessment",
        "review",
        "overpressure",
        "health check",
        "report on",
        "status of",
    ]

    # ========================================================
    # CALCULATION KEYWORDS
    # ========================================================

    CALCULATION_KEYWORDS = [
        "calculate",
        "calculation",
        "compute",
        "percentage",
        "percent",
        "deviation",
        "difference",
        "increase",
        "decrease",
        "average",
        "mean",
        "median",
        "minimum",
        "maximum",
        "variance",
        "standard deviation",
        "std dev",
        "percentile",
        "ratio",
        "total",
        "trend",
        "moving average",
        "change",
        "water cut",
        "watercut",
        "total liquid rate",
        "total liquid",
        "gas oil ratio",
        "gas-oil ratio",
        "gor",
        "pump efficiency",
        "mtbf",
        "mttr",
        "equipment availability",
        "above the limit",
        "below the limit",
        "operating limit",
        "threshold",
    ]

    # ========================================================
    # DOCUMENT CREATION KEYWORDS
    # ========================================================

    CREATE_DOC_KEYWORDS = [
        "create a document",
        "create an approval",
        "create a report",
        "create a technical",
        "create an inspection",
        "create a risk",
        "create the risk",
        "generate a document",
        "generate an approval",
        "generate a report",
        "generate technical",
        "generate an inspection",
        "generate a risk",
        "generate the risk",
        "generate a management",
        "prepare an approval",
        "prepare a report",
        "prepare a technical",
        "prepare an inspection",
        "prepare a risk",
        "prepare a management",
        "write an approval",
        "write the approval",
        "draft an approval",
        "draft a report",
        "draft the report",
        "draft a technical",
        "draft an inspection",
        "approval note",
        "technical review document",
        "inspection report for",
        "risk assessment document",
        "management summary document",
        "document for approval",
        "approval document",
        "make a ppt",
        "make a slide",
        "make a presentation",
        "put it in a sheet",
        "make a csv",
        "put this in excel",
        "generate a spreadsheet",
        "create a spreadsheet",
        "in a sheet",
        "as a ppt",
        "in excel",
    ]

    # ========================================================
    # DOCUMENT UPDATE KEYWORDS
    # ========================================================

    UPDATE_DOC_KEYWORDS = [
        "update the document",
        "update the artifact",
        "edit the document",
        "edit the artifact",
        "revise the document",
        "revise the artifact",
        "update the report",
        "edit the report",
        "add a section",
        "add another section",
        "expand the",
        "make a version",
        "new version of",
        "change the document",
        "revise the approval",
        "update the approval",
        "update the",
        "make changes to",
        "modify the",
        "draft a revision",
        "changes to the document",
        "add a note",
        "add an appendix",
        "add the recommendation",
        "add a recommendation",
        "include a section",
        "extend the document",
    ]

    ADD_SECTION_RE = re.compile(
        r"add a "
        r"(risk|mitigation|recommendation|section|note|appendix|"
        r"paragraph|slide|sheet|finding|comment)"
    )

    # ========================================================
    # DOCUMENT CONVERSION KEYWORDS
    # ========================================================

    CONVERT_DOC_KEYWORDS = [
        "convert the document",
        "convert the artifact",
        "convert to",
        "convert it to",
        "change format to",
        "turn it into a pdf",
        "as a pdf instead",
        "convert the report to",
        "convert to pdf",
        "convert to excel",
        "convert to csv",
        "convert to json",
        "convert to ppt",
        "convert the",
        "turn it into",
        "in pdf format",
        "as a pdf",
        "as a csv",
        "as a json",
        "turn it into a",
        "turn it into an",
        "as an excel",
        "into a pdf",
        "into an excel",
    ]

    CONVERT_RE = re.compile(
        r"(convert|turn|change)\b[^.]*\b(?:to|into)\b\s+"
        r"(?:an?\s+)?"
        r"(pdf|docx|xlsx|csv|json|md|txt|pptx|word|excel|powerpoint|slides)"
        r"|"
        r"(pdf|docx|xlsx|csv|json|md|txt|pptx)\b\s+instead"
        r"|"
        r"to\s+(pdf|docx|xlsx|csv|json|md|txt)\b\s+format"
    )

    # ========================================================
    # CODE KEYWORDS
    # ========================================================

    CODE_KEYWORDS = [
        "write a python",
        "write python",
        "python script",
        "python code",
        "run a python",
        "run python",
        "script to compute",
        "script that computes",
        "write a script",
        "script to calculate",
        "script that calculates",
        "compute with code",
        "calculate using code",
        "simulate",
        "simulation",
        "write me code",
        "generate code",
        "write code",
    ]

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(self):
        self.model = settings.primary_model

    # ========================================================
    # MAIN PLAN CREATION
    # ========================================================

    async def create_plan(
        self,
        state: AgentState
    ) -> AgentPlan:

        return self._fallback_plan(state)

    # ========================================================
    # ARTIFACT ID RESOLUTION
    # ========================================================

    def _resolve_artifact_id(
        self,
        context: Dict[str, Any]
    ) -> Optional[str]:

        if not context:
            return None

        artifacts = context.get("artifacts")

        if artifacts and isinstance(artifacts, list):

            if isinstance(artifacts[0], dict):
                return artifacts[0].get(
                    "artifact_id"
                )

            return str(artifacts[0])

        return None

    # ========================================================
    # NUMBER EXTRACTION
    # ========================================================

    def _extract_rate(
        self,
        query_lower: str,
        keywords: List[str]
    ) -> Optional[float]:

        """
        Extract a numerical value associated with one of the
        supplied keywords.

        Examples:

        oil rate 800 BPD
        oil 800 BPD
        water rate = 200 BPD
        gas rate 5000 SCF/day
        """

        keyword_pattern = "|".join(
            re.escape(keyword)
            for keyword in keywords
        )

        pattern = re.compile(
            rf"(?:{keyword_pattern})"
            rf"\s*(?:rate)?"
            rf"\s*(?:is|=|of|:)?"
            rf"\s*(-?\d+(?:\.\d+)?)",
            re.IGNORECASE
        )

        match = pattern.search(query_lower)

        if match:
            try:
                return float(match.group(1))
            except (TypeError, ValueError):
                return None

        return None

    # ========================================================
    # UNIT EXTRACTION
    # ========================================================

    def _extract_unit(
        self,
        query_lower: str,
        default: str
    ) -> str:

        if "bpd" in query_lower:
            return "BPD"

        if "m3/day" in query_lower:
            return "m3/day"

        if "m³/day" in query_lower:
            return "m³/day"

        if "mmscf" in query_lower:
            return "MMSCF"

        if "mscf" in query_lower:
            return "MSCF"

        if "scf" in query_lower:
            return "SCF"

        return default

    # ========================================================
    # DETECT CALCULATION TYPE
    # ========================================================

    def _detect_calculation_operation(
        self,
        query_lower: str
    ) -> str:

        # ----------------------------------------------------
        # Petroleum production calculations
        # ----------------------------------------------------

        if (
            "water cut" in query_lower
            or "watercut" in query_lower
        ):
            return "water_cut"

        if (
            "total liquid rate" in query_lower
            or "total liquid" in query_lower
            or "liquid rate" in query_lower
        ):
            return "total_liquid_rate"

        if (
            "gas oil ratio" in query_lower
            or "gas-oil ratio" in query_lower
            or re.search(r"\bgor\b", query_lower)
        ):
            return "gas_oil_ratio"

        # ----------------------------------------------------
        # Equipment performance calculations
        # ----------------------------------------------------

        if "pump efficiency" in query_lower:
            return "pump_efficiency"

        if re.search(r"\bmtbf\b", query_lower):
            return "mtbf"

        if re.search(r"\bmttr\b", query_lower):
            return "mttr"

        if "equipment availability" in query_lower:
            return "equipment_availability"

        # ----------------------------------------------------
        # Percentage deviation
        # ----------------------------------------------------

        if (
            "percentage deviation" in query_lower
            or "percent deviation" in query_lower
            or "percentage above" in query_lower
            or "percentage below" in query_lower
            or "% above" in query_lower
            or "% below" in query_lower
        ):
            return "percentage_deviation"

        # ----------------------------------------------------
        # Absolute deviation / difference
        # ----------------------------------------------------

        if (
            "absolute deviation" in query_lower
            or "deviation" in query_lower
            or "difference" in query_lower
            or "how far" in query_lower
            or "above its limit" in query_lower
            or "below its limit" in query_lower
        ):
            return "absolute_deviation"

        # ----------------------------------------------------
        # Percentage change
        # ----------------------------------------------------

        if (
            "percentage change" in query_lower
            or "percentage increase" in query_lower
            or "percentage decrease" in query_lower
            or "percent increase" in query_lower
            or "percent decrease" in query_lower
        ):
            return "percentage_change"

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        if (
            "average" in query_lower
            or "mean" in query_lower
            or "median" in query_lower
            or "variance" in query_lower
            or "standard deviation" in query_lower
            or "std dev" in query_lower
            or "percentile" in query_lower
            or "statistics" in query_lower
        ):
            return "statistics"

        # ----------------------------------------------------
        # Trend
        # ----------------------------------------------------

        if (
            "trend" in query_lower
            or "moving average" in query_lower
            or "period over period" in query_lower
            or "historical change" in query_lower
            or "historical changes" in query_lower
        ):
            return "trend"

        # ----------------------------------------------------
        # Ratio
        # ----------------------------------------------------

        if "ratio" in query_lower:
            return "ratio"

        # ----------------------------------------------------
        # Default calculation
        # ----------------------------------------------------

        return "absolute_deviation"

    # ========================================================
    # CREATE STRUCTURED CALCULATION PLAN
    # ========================================================

    def _create_calculation_step(
        self,
        state: AgentState,
        operation: str
    ) -> AgentStepModel:

        """
        Create a structured calculation step.

        The planner identifies the calculation operation and
        prepares structured inputs.

        Numerical arithmetic itself is NEVER performed here.
        The Calculation Engine performs the deterministic
        calculation.
        """

        query_lower = state.query.lower()

        # ====================================================
        # PETROLEUM: WATER CUT
        # ====================================================

        if operation == "water_cut":

            oil_rate = self._extract_rate(
                query_lower,
                ["oil rate", "oil"]
            )

            water_rate = self._extract_rate(
                query_lower,
                ["water rate", "water"]
            )

            unit = self._extract_unit(
                query_lower,
                "BPD"
            )

            # If both values are explicitly present, use them.
            if oil_rate is not None and water_rate is not None:

                return AgentStepModel(
                    label="Calculate water cut using Calculation Engine",
                    tool="calculate",
                    input_data={
                        "operation": "water_cut",
                        "inputs": {
                            "oil_rate": {
                                "value": oil_rate,
                                "unit": unit,
                                "source": "User-provided input"
                            },
                            "water_rate": {
                                "value": water_rate,
                                "unit": unit,
                                "source": "User-provided input"
                            }
                        },
                        "context": {
                            "parameter": "water_cut",
                            "source_type": "user_input"
                        }
                    }
                )

            # Missing values must NOT be invented.
            return AgentStepModel(
                label="Retrieve missing petroleum production inputs",
                tool="search_documents",
                input_data={
                    "query": state.query,
                    "limit": 10,
                }
            )

        # ====================================================
        # PETROLEUM: TOTAL LIQUID RATE
        # ====================================================

        if operation == "total_liquid_rate":

            oil_rate = self._extract_rate(
                query_lower,
                ["oil rate", "oil"]
            )

            water_rate = self._extract_rate(
                query_lower,
                ["water rate", "water"]
            )

            unit = self._extract_unit(
                query_lower,
                "BPD"
            )

            if oil_rate is not None and water_rate is not None:

                return AgentStepModel(
                    label="Calculate total liquid rate using Calculation Engine",
                    tool="calculate",
                    input_data={
                        "operation": "total_liquid_rate",
                        "inputs": {
                            "oil_rate": {
                                "value": oil_rate,
                                "unit": unit,
                                "source": "User-provided input"
                            },
                            "water_rate": {
                                "value": water_rate,
                                "unit": unit,
                                "source": "User-provided input"
                            }
                        },
                        "context": {
                            "parameter": "total_liquid_rate",
                            "source_type": "user_input"
                        }
                    }
                )

            return AgentStepModel(
                label="Retrieve missing petroleum production inputs",
                tool="search_documents",
                input_data={
                    "query": state.query,
                    "limit": 10,
                }
            )

        # ====================================================
        # PETROLEUM: GAS-OIL RATIO
        # ====================================================

        if operation == "gas_oil_ratio":

            gas_rate = self._extract_rate(
                query_lower,
                ["gas rate", "gas"]
            )

            oil_rate = self._extract_rate(
                query_lower,
                ["oil rate", "oil"]
            )

            gas_unit = self._extract_unit(
                query_lower,
                "SCF"
            )

            oil_unit = "BPD"

            if gas_rate is not None and oil_rate is not None:

                return AgentStepModel(
                    label="Calculate gas-oil ratio using Calculation Engine",
                    tool="calculate",
                    input_data={
                        "operation": "gas_oil_ratio",
                        "inputs": {
                            "gas_rate": {
                                "value": gas_rate,
                                "unit": gas_unit,
                                "source": "User-provided input"
                            },
                            "oil_rate": {
                                "value": oil_rate,
                                "unit": oil_unit,
                                "source": "User-provided input"
                            }
                        },
                        "context": {
                            "parameter": "gas_oil_ratio",
                            "source_type": "user_input"
                        }
                    }
                )

            return AgentStepModel(
                label="Retrieve missing petroleum production inputs",
                tool="search_documents",
                input_data={
                    "query": state.query,
                    "limit": 10,
                }
            )

        # ====================================================
        # EQUIPMENT: PUMP EFFICIENCY
        # ====================================================

        if operation == "pump_efficiency":

            hydraulic_power = self._extract_rate(
                query_lower,
                [
                    "hydraulic power",
                    "hydraulic"
                ]
            )

            input_power = self._extract_rate(
                query_lower,
                [
                    "input power",
                    "input"
                ]
            )

            if (
                hydraulic_power is not None
                and input_power is not None
            ):

                return AgentStepModel(
                    label="Calculate pump efficiency using Calculation Engine",
                    tool="calculate",
                    input_data={
                        "operation": "pump_efficiency",
                        "inputs": {
                            "hydraulic_power": {
                                "value": hydraulic_power,
                                "unit": "kW",
                                "source": "User-provided input"
                            },
                            "input_power": {
                                "value": input_power,
                                "unit": "kW",
                                "source": "User-provided input"
                            }
                        },
                        "context": {
                            "parameter": "pump_efficiency",
                            "source_type": "user_input"
                        }
                    }
                )

            return AgentStepModel(
                label="Retrieve missing pump efficiency inputs",
                tool="search_documents",
                input_data={
                    "query": state.query,
                    "limit": 10,
                }
            )

        # ====================================================
        # EQUIPMENT: MTBF
        # ====================================================

        if operation == "mtbf":

            operating_time = self._extract_rate(
                query_lower,
                [
                    "total operating time",
                    "operating time",
                    "operating hours"
                ]
            )

            failures = self._extract_rate(
                query_lower,
                [
                    "number of failures",
                    "failures"
                ]
            )

            if (
                operating_time is not None
                and failures is not None
            ):

                return AgentStepModel(
                    label="Calculate MTBF using Calculation Engine",
                    tool="calculate",
                    input_data={
                        "operation": "mtbf",
                        "inputs": {
                            "total_operating_time": {
                                "value": operating_time,
                                "unit": "hours",
                                "source": "User-provided input"
                            },
                            "number_of_failures": {
                                "value": failures,
                                "unit": "count",
                                "source": "User-provided input"
                            }
                        },
                        "context": {
                            "parameter": "mtbf",
                            "source_type": "user_input"
                        }
                    }
                )

            return AgentStepModel(
                label="Retrieve missing MTBF inputs",
                tool="search_documents",
                input_data={
                    "query": state.query,
                    "limit": 10,
                }
            )

        # ====================================================
        # EQUIPMENT: MTTR
        # ====================================================

        if operation == "mttr":

            repair_time = self._extract_rate(
                query_lower,
                [
                    "total repair time",
                    "repair time",
                    "repair hours"
                ]
            )

            repairs = self._extract_rate(
                query_lower,
                [
                    "number of repairs",
                    "repairs"
                ]
            )

            if (
                repair_time is not None
                and repairs is not None
            ):

                return AgentStepModel(
                    label="Calculate MTTR using Calculation Engine",
                    tool="calculate",
                    input_data={
                        "operation": "mttr",
                        "inputs": {
                            "total_repair_time": {
                                "value": repair_time,
                                "unit": "hours",
                                "source": "User-provided input"
                            },
                            "number_of_repairs": {
                                "value": repairs,
                                "unit": "count",
                                "source": "User-provided input"
                            }
                        },
                        "context": {
                            "parameter": "mttr",
                            "source_type": "user_input"
                        }
                    }
                )

            return AgentStepModel(
                label="Retrieve missing MTTR inputs",
                tool="search_documents",
                input_data={
                    "query": state.query,
                    "limit": 10,
                }
            )

        # ====================================================
        # EQUIPMENT: AVAILABILITY
        # ====================================================

        if operation == "equipment_availability":

            operating_time = self._extract_rate(
                query_lower,
                [
                    "operating time",
                    "operating hours"
                ]
            )

            downtime = self._extract_rate(
                query_lower,
                [
                    "downtime",
                    "down time"
                ]
            )

            if (
                operating_time is not None
                and downtime is not None
            ):

                return AgentStepModel(
                    label="Calculate equipment availability using Calculation Engine",
                    tool="calculate",
                    input_data={
                        "operation": "equipment_availability",
                        "inputs": {
                            "operating_time": {
                                "value": operating_time,
                                "unit": "hours",
                                "source": "User-provided input"
                            },
                            "downtime": {
                                "value": downtime,
                                "unit": "hours",
                                "source": "User-provided input"
                            }
                        },
                        "context": {
                            "parameter": "equipment_availability",
                            "source_type": "user_input"
                        }
                    }
                )

            return AgentStepModel(
                label="Retrieve missing equipment availability inputs",
                tool="search_documents",
                input_data={
                    "query": state.query,
                    "limit": 10,
                }
            )

        # ====================================================
        # P-102 DEMONSTRATION / ENGINEERING CALCULATIONS
        # ====================================================

        if "p-102" in query_lower or "pressure" in query_lower:

            # ------------------------------------------------
            # Percentage change
            # ------------------------------------------------

            if operation == "percentage_change":

                return AgentStepModel(
                    label="Calculate pressure percentage change",
                    tool="calculate",
                    input_data={
                        "operation": "percentage_change",
                        "inputs": {
                            "previous": {
                                "value": 34,
                                "unit": "bar",
                                "source": "P-102 historical records"
                            },
                            "current": {
                                "value": 42,
                                "unit": "bar",
                                "source": "P-102 inspection 2026"
                            }
                        },
                        "context": {
                            "asset_id": "P-102",
                            "parameter": "pressure",
                            "source_type": "prototype_demo"
                        }
                    }
                )

            # ------------------------------------------------
            # Trend
            # ------------------------------------------------

            if operation == "trend":

                return AgentStepModel(
                    label="Calculate P-102 pressure trend",
                    tool="calculate",
                    input_data={
                        "operation": "trend",
                        "inputs": {},
                        "dataset": [
                            {
                                "period": "2024",
                                "value": 34,
                                "unit": "bar",
                                "source": "P-102 historical records"
                            },
                            {
                                "period": "2025",
                                "value": 37,
                                "unit": "bar",
                                "source": "P-102 historical records"
                            },
                            {
                                "period": "2026",
                                "value": 42,
                                "unit": "bar",
                                "source": "P-102 inspection 2026"
                            }
                        ],
                        "context": {
                            "asset_id": "P-102",
                            "parameter": "pressure",
                            "source_type": "prototype_demo"
                        }
                    }
                )

            # ------------------------------------------------
            # Statistics
            # ------------------------------------------------

            if operation == "statistics":

                return AgentStepModel(
                    label="Calculate P-102 pressure statistics",
                    tool="calculate",
                    input_data={
                        "operation": "statistics",
                        "inputs": {},
                        "dataset": [
                            {
                                "period": "2024",
                                "value": 34,
                                "unit": "bar",
                                "source": "P-102 historical records"
                            },
                            {
                                "period": "2025",
                                "value": 37,
                                "unit": "bar",
                                "source": "P-102 historical records"
                            },
                            {
                                "period": "2026",
                                "value": 42,
                                "unit": "bar",
                                "source": "P-102 inspection 2026"
                            }
                        ],
                        "context": {
                            "asset_id": "P-102",
                            "parameter": "pressure",
                            "source_type": "prototype_demo"
                        }
                    }
                )

            # ------------------------------------------------
            # Percentage deviation
            # ------------------------------------------------

            if operation == "percentage_deviation":

                return AgentStepModel(
                    label="Calculate pressure percentage deviation",
                    tool="calculate",
                    input_data={
                        "operation": "percentage_deviation",
                        "inputs": {
                            "actual": {
                                "value": 42,
                                "unit": "bar",
                                "source": "P-102 inspection 2026"
                            },
                            "reference": {
                                "value": 40,
                                "unit": "bar",
                                "source": "Pump operating SOP"
                            }
                        },
                        "context": {
                            "asset_id": "P-102",
                            "parameter": "pressure",
                            "source_type": "prototype_demo"
                        }
                    }
                )

            # ------------------------------------------------
            # Absolute deviation
            # ------------------------------------------------

            return AgentStepModel(
                label="Calculate pressure deviation",
                tool="calculate",
                input_data={
                    "operation": "absolute_deviation",
                    "inputs": {
                        "actual": {
                            "value": 42,
                            "unit": "bar",
                            "source": "P-102 inspection 2026"
                        },
                        "reference": {
                            "value": 40,
                            "unit": "bar",
                            "source": "Pump operating SOP"
                        }
                    },
                    "context": {
                        "asset_id": "P-102",
                        "parameter": "pressure",
                        "source_type": "prototype_demo"
                    }
                }
            )

        # ====================================================
        # GENERIC CALCULATION
        # ====================================================

        return AgentStepModel(
            label=f"Execute {operation} using Calculation Engine",
            tool="calculate",
            input_data={
                "operation": operation,
                "inputs": {},
                "context": {
                    "query": state.query
                }
            }
        )

    # ========================================================
    # FALLBACK PLAN
    # ========================================================

    def _fallback_plan(
        self,
        state: AgentState
    ) -> AgentPlan:

        query_lower = state.query.lower()

        steps: List[AgentStepModel] = []

        # ----------------------------------------------------
        # Detect intent
        # ----------------------------------------------------

        wants_analysis = any(
            kw in query_lower
            for kw in self.ANALYSIS_KEYWORDS
        )

        wants_calculation = any(
            kw in query_lower
            for kw in self.CALCULATION_KEYWORDS
        )

        wants_doc = any(
            kw in query_lower
            for kw in self.CREATE_DOC_KEYWORDS
        )

        wants_code = any(
            kw in query_lower
            for kw in self.CODE_KEYWORDS
        )

        wants_update = (
            any(
                kw in query_lower
                for kw in self.UPDATE_DOC_KEYWORDS
            )
            or bool(
                self.ADD_SECTION_RE.search(
                    query_lower
                )
            )
        )

        wants_convert = (
            any(
                kw in query_lower
                for kw in self.CONVERT_DOC_KEYWORDS
            )
            or bool(
                self.CONVERT_RE.search(
                    query_lower
                )
            )
        )

        # ----------------------------------------------------
        # UPDATE ARTIFACT
        # ----------------------------------------------------

        if wants_update:

            artifact_id = self._resolve_artifact_id(
                state.context
            )

            steps.append(
                AgentStepModel(
                    label="Update generated artifact (new version)",
                    tool="update_artifact",
                    input_data={
                        "artifact_id": artifact_id,
                        "change_instruction": state.query,
                    },
                )
            )

        # ----------------------------------------------------
        # CONVERT ARTIFACT
        # ----------------------------------------------------

        elif wants_convert:

            artifact_id = self._resolve_artifact_id(
                state.context
            )

            target = self._detect_convert_format(
                query_lower
            )

            steps.append(
                AgentStepModel(
                    label="Convert artifact to new format",
                    tool="convert_artifact",
                    input_data={
                        "artifact_id": artifact_id,
                        "format": target,
                    },
                )
            )

        # ----------------------------------------------------
        # CREATE DOCUMENT
        # ----------------------------------------------------

        elif wants_doc:

            steps.append(
                AgentStepModel(
                    label="Generate company document",
                    tool="generate_document",
                    input_data={
                        "query": state.query,
                        "template": None,
                        "format": None,
                    },
                )
            )

        # ----------------------------------------------------
        # CODE REQUEST
        # ----------------------------------------------------

        elif wants_code:

            steps.append(
                AgentStepModel(
                    label="Write and run Python in the sandbox",
                    tool="coding_agent",
                    input_data={
                        "query": state.query,
                        "timeout": 30,
                    },
                )
            )

        # ----------------------------------------------------
        # CALCULATION / ENGINEERING REQUEST
        # ----------------------------------------------------

        elif wants_calculation:

            # -----------------------------------------------
            # Search authoritative evidence FIRST
            # -----------------------------------------------

            steps.append(
                AgentStepModel(
                    label="Search authoritative documents and evidence",
                    tool="search_documents",
                    input_data={
                        "query": state.query,
                        "limit": 10,
                    },
                )
            )

            # -----------------------------------------------
            # Structured analysis when requested
            # -----------------------------------------------

            if wants_analysis:
                steps.append(
                    AgentStepModel(
                        label="Analyze retrieved structured data",
                        tool="analyze_data",
                        input_data={
                            "query": state.query,
                            "asset_id": None,
                        },
                    )
                )

            # -----------------------------------------------
            # Determine calculation operation
            # -----------------------------------------------

            operation = self._detect_calculation_operation(
                query_lower
            )

            # -----------------------------------------------
            # Add deterministic calculation
            # -----------------------------------------------

            steps.append(
                self._create_calculation_step(
                    state,
                    operation
                )
            )

        # ----------------------------------------------------
        # EXISTING ASSET / KNOWLEDGE FLOW
        # ----------------------------------------------------

        else:

            if any(
                kw in query_lower
                for kw in [
                    "pressure",
                    "corrosion",
                    "vibration",
                    "inspection",
                    "p-102",
                    "asset",
                ]
            ):

                steps.append(
                    AgentStepModel(
                        label="Search for relevant documents",
                        tool="search_documents",
                        input_data={
                            "query": state.query,
                            "limit": 10,
                        },
                    )
                )

            if wants_analysis:

                steps.append(
                    AgentStepModel(
                        label="Run structured data analysis",
                        tool="analyze_data",
                        input_data={
                            "query": state.query,
                            "asset_id": None,
                        },
                    )
                )

            if not steps:

                steps.append(
                    AgentStepModel(
                        label="Search knowledge base",
                        tool="search_documents",
                        input_data={
                            "query": state.query,
                            "limit": 5,
                        },
                    )
                )

        # ----------------------------------------------------
        # FINAL SYNTHESIS STEP
        # ----------------------------------------------------

        steps.append(
            AgentStepModel(
                label="Synthesize answer",
                tool=None,
                input_data={},
            )
        )

        # ----------------------------------------------------
        # CREATE PLAN
        # ----------------------------------------------------

        plan = AgentPlan(
            steps=steps
        )

        state.plan = plan
        state.phase = AgentPhase.TOOL_EXECUTION

        return plan

    # ========================================================
    # CONVERSION FORMAT DETECTION
    # ========================================================

    def _detect_convert_format(
        self,
        query_lower: str
    ) -> str:

        for fmt, hints in {

            "pdf": [
                "pdf"
            ],

            "docx": [
                "word",
                "docx"
            ],

            "xlsx": [
                "excel",
                "xlsx",
                "spreadsheet",
                "a sheet"
            ],

            "pptx": [
                "powerpoint",
                "pptx",
                "slides",
                "deck",
                "a ppt"
            ],

            "csv": [
                "csv"
            ],

            "json": [
                "json"
            ],

            "md": [
                "markdown",
                ".md"
            ],

            "txt": [
                "txt"
            ],

        }.items():

            if any(
                hint in query_lower
                for hint in hints
            ):
                return fmt

        return "pdf"


# ============================================================
# GLOBAL PLANNER INSTANCE
# ============================================================

planner = Planner()