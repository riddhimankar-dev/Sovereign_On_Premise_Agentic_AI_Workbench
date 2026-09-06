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

Calculation examples:

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
        "sum",
        "trend",
        "moving average",
        "change",
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
    # DETECT CALCULATION TYPE
    # ========================================================

    def _detect_calculation_operation(
        self,
        query_lower: str
    ) -> str:

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

        IMPORTANT:
        The planner does not perform arithmetic.

        The actual numerical values should come from
        retrieval/document analysis/RAG context.

        For the P-102 prototype, the known demonstration
        values are used as fallback inputs. These should
        eventually be replaced by retrieved evidence.
        """

        query_lower = state.query.lower()

        # ----------------------------------------------------
        # P-102 demonstration values
        #
        # These are the values specified in the Calculation
        # Engine specification:
        #
        # Actual pressure = 42 bar
        # Maximum operating pressure = 40 bar
        # ----------------------------------------------------

        if "p-102" in query_lower or "pressure" in query_lower:

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

        # ----------------------------------------------------
        # Generic calculation request
        #
        # IMPORTANT:
        # Don't invent values for generic calculations.
        # Let retrieval/agent flow provide the values.
        # ----------------------------------------------------

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