from typing import Any, Dict, List


class CostEngine:
    """
    Deterministic Engineering Cost Intelligence Engine.

    Performs project cost estimation, budget analysis,
    and what-if scenario analysis.

    No LLM is used for numerical calculations.
    """

    VERSION = "1.0"

    # Contingency rates based on engineering risk
    CRITICALITY_CONTINGENCY = {
        "low": 0.00,
        "medium": 0.02,
        "high": 0.03,
        "critical": 0.05,
    }

    # Additional contingency for safety-critical equipment
    SAFETY_CRITICAL_CONTINGENCY = 0.02

    # Budget variance thresholds
    LOW_VARIANCE = 5.0
    MEDIUM_VARIANCE = 10.0

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    @staticmethod
    def _number(value: Any, field_name: str) -> float:
        """
        Convert a value to a non-negative number.
        """

        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{field_name} must be a numeric value"
            )

        if number < 0:
            raise ValueError(
                f"{field_name} cannot be negative"
            )

        return number

    # ---------------------------------------------------------
    # SINGLE ITEM CALCULATION
    # ---------------------------------------------------------

    @classmethod
    def _calculate_item(
        cls,
        item: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculate the cost of one engineering/BOM item.
        """

        name = item.get(
            "name",
            "Unnamed Item",
        )

        quantity = cls._number(
            item.get("quantity", 0),
            f"{name}.quantity",
        )

        unit_cost = cls._number(
            item.get("unit_cost", 0),
            f"{name}.unit_cost",
        )

        installation_unit_cost = cls._number(
            item.get("installation_cost", 0),
            f"{name}.installation_cost",
        )

        maintenance_unit_cost = cls._number(
            item.get("maintenance_cost", 0),
            f"{name}.maintenance_cost",
        )

        # -----------------------------------------------------
        # BASIC COSTS
        # -----------------------------------------------------

        equipment_cost = (
            quantity * unit_cost
        )

        installation_cost = (
            quantity * installation_unit_cost
        )

        maintenance_cost = (
            quantity * maintenance_unit_cost
        )

        base_cost = (
            equipment_cost
            + installation_cost
            + maintenance_cost
        )

        # -----------------------------------------------------
        # CONTINGENCY
        # -----------------------------------------------------

        criticality = str(
            item.get(
                "criticality",
                "low",
            )
        ).lower()

        if criticality not in cls.CRITICALITY_CONTINGENCY:
            raise ValueError(
                f"Invalid criticality '{criticality}' "
                f"for item '{name}'. "
                f"Allowed values: "
                f"{', '.join(cls.CRITICALITY_CONTINGENCY.keys())}"
            )

        criticality_rate = (
            cls.CRITICALITY_CONTINGENCY[
                criticality
            ]
        )

        safety_critical = bool(
            item.get(
                "safety_critical",
                False,
            )
        )

        safety_rate = (
            cls.SAFETY_CRITICAL_CONTINGENCY
            if safety_critical
            else 0.0
        )

        contingency_rate = (
            criticality_rate
            + safety_rate
        )

        contingency = (
            base_cost * contingency_rate
        )

        total_cost = (
            base_cost + contingency
        )

        return {
            "name": name,
            "category": item.get("category"),
            "material": item.get("material"),

            "quantity": quantity,
            "unit_cost": unit_cost,

            "installation_unit_cost": (
                installation_unit_cost
            ),

            "maintenance_unit_cost": (
                maintenance_unit_cost
            ),

            "criticality": criticality,
            "safety_critical": safety_critical,

            "equipment_cost": round(
                equipment_cost,
                2,
            ),

            "installation_cost": round(
                installation_cost,
                2,
            ),

            "maintenance_cost": round(
                maintenance_cost,
                2,
            ),

            "base_cost": round(
                base_cost,
                2,
            ),

            "contingency_rate": round(
                contingency_rate * 100,
                2,
            ),

            "contingency": round(
                contingency,
                2,
            ),

            "total_cost": round(
                total_cost,
                2,
            ),
        }

    # ---------------------------------------------------------
    # COST ESTIMATE
    # ---------------------------------------------------------

    @classmethod
    def estimate(
        cls,
        project_name: str,
        budget: float,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate a complete project cost estimate.
        """

        if not project_name or not project_name.strip():
            raise ValueError(
                "project_name is required"
            )

        budget = cls._number(
            budget,
            "budget",
        )

        if budget <= 0:
            raise ValueError(
                "budget must be greater than zero"
            )

        if not items:
            raise ValueError(
                "At least one cost item is required"
            )

        calculated_items = []

        for item in items:
            calculated_items.append(
                cls._calculate_item(item)
            )

        # -----------------------------------------------------
        # TOTALS
        # -----------------------------------------------------

        equipment_total = sum(
            item["equipment_cost"]
            for item in calculated_items
        )

        installation_total = sum(
            item["installation_cost"]
            for item in calculated_items
        )

        maintenance_total = sum(
            item["maintenance_cost"]
            for item in calculated_items
        )

        base_total = sum(
            item["base_cost"]
            for item in calculated_items
        )

        contingency_total = sum(
            item["contingency"]
            for item in calculated_items
        )

        total_cost = sum(
            item["total_cost"]
            for item in calculated_items
        )

        # -----------------------------------------------------
        # BUDGET VARIANCE
        # -----------------------------------------------------

        variance = (
            total_cost - budget
        )

        variance_percentage = (
            variance / budget
        ) * 100

        risk_level = cls._risk_level(
            variance_percentage
        )

        budget_status = cls._budget_status(
            variance_percentage
        )

        return {
            "engine_version": cls.VERSION,

            "project_name": project_name,

            "budget": round(
                budget,
                2,
            ),

            "items": calculated_items,

            "summary": {
                "equipment_cost": round(
                    equipment_total,
                    2,
                ),

                "installation_cost": round(
                    installation_total,
                    2,
                ),

                "maintenance_cost": round(
                    maintenance_total,
                    2,
                ),

                "base_cost": round(
                    base_total,
                    2,
                ),

                "contingency": round(
                    contingency_total,
                    2,
                ),

                "total_estimated_cost": round(
                    total_cost,
                    2,
                ),

                "variance": round(
                    variance,
                    2,
                ),

                "variance_percentage": round(
                    variance_percentage,
                    2,
                ),

                "risk_level": risk_level,

                "budget_status": budget_status,
            },

            "calculation_trace": {
                "formula": (
                    "Total Cost = "
                    "Equipment Cost + "
                    "Installation Cost + "
                    "Maintenance Cost + "
                    "Contingency"
                ),

                "equipment_formula": (
                    "quantity × unit_cost"
                ),

                "installation_formula": (
                    "quantity × installation_unit_cost"
                ),

                "maintenance_formula": (
                    "quantity × maintenance_unit_cost"
                ),

                "variance_formula": (
                    "total_estimated_cost - budget"
                ),

                "variance_percentage_formula": (
                    "(variance / budget) × 100"
                ),

                "contingency_policy": {
                    "criticality": (
                        "low=0%, medium=2%, "
                        "high=3%, critical=5%"
                    ),
                    "safety_critical": (
                        "additional 2%"
                    ),
                },
            },
        }

    # ---------------------------------------------------------
    # BUDGET ANALYSIS
    # ---------------------------------------------------------

    @classmethod
    def budget_analysis(
        cls,
        project_name: str,
        budget: float,
        items: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze estimated project cost against budget.
        """

        estimate = cls.estimate(
            project_name=project_name,
            budget=budget,
            items=items,
        )

        summary = estimate["summary"]

        estimated_cost = summary[
            "total_estimated_cost"
        ]

        budget_value = estimate["budget"]

        budget_utilization = (
            estimated_cost / budget_value
        ) * 100

        remaining_budget = (
            budget_value - estimated_cost
        )

        return {
            "project_name": project_name,

            "budget": budget_value,

            "estimated_cost": estimated_cost,

            "variance": summary[
                "variance"
            ],

            "variance_percentage": summary[
                "variance_percentage"
            ],

            "risk_level": summary[
                "risk_level"
            ],

            "budget_status": summary[
                "budget_status"
            ],

            "budget_utilization_percentage": round(
                budget_utilization,
                2,
            ),

            "remaining_budget": round(
                remaining_budget,
                2,
            ),

            "recommendation": cls._recommendation(
                summary["variance_percentage"]
            ),
        }

    # ---------------------------------------------------------
    # WHAT-IF ANALYSIS
    # ---------------------------------------------------------

    @classmethod
    def what_if(
        cls,
        project_name: str,
        budget: float,
        items: List[Dict[str, Any]],
        changes: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compare the baseline estimate with a modified
        what-if scenario.
        """

        baseline = cls.estimate(
            project_name=project_name,
            budget=budget,
            items=items,
        )

        # Deep enough copy for our flat item dictionaries
        modified_items = [
            dict(item)
            for item in items
        ]

        item_changes = changes.get(
            "items",
            [],
        )

        allowed_fields = {
            "quantity",
            "unit_cost",
            "installation_cost",
            "maintenance_cost",
            "criticality",
            "safety_critical",
            "name",
            "category",
            "material",
        }

        for change in item_changes:

            index = change.get("index")

            if index is None:
                raise ValueError(
                    "Each what-if item change "
                    "requires an index"
                )

            if not isinstance(index, int):
                raise ValueError(
                    "What-if item index "
                    "must be an integer"
                )

            if (
                index < 0
                or index >= len(modified_items)
            ):
                raise ValueError(
                    f"Invalid item index: {index}"
                )

            for field, value in change.items():

                if field == "index":
                    continue

                if field not in allowed_fields:
                    raise ValueError(
                        f"Unsupported what-if field: "
                        f"{field}"
                    )

                modified_items[index][
                    field
                ] = value

        scenario_budget = changes.get(
            "budget",
            budget,
        )

        scenario = cls.estimate(
            project_name=project_name,
            budget=scenario_budget,
            items=modified_items,
        )

        baseline_cost = baseline[
            "summary"
        ]["total_estimated_cost"]

        scenario_cost = scenario[
            "summary"
        ]["total_estimated_cost"]

        cost_difference = (
            scenario_cost - baseline_cost
        )

        baseline_variance = baseline[
            "summary"
        ]["variance"]

        scenario_variance = scenario[
            "summary"
        ]["variance"]

        if cost_difference > 0:
            direction = "increase"
        elif cost_difference < 0:
            direction = "decrease"
        else:
            direction = "no_change"

        if baseline_cost:
            cost_difference_percentage = (
                cost_difference
                / baseline_cost
            ) * 100
        else:
            cost_difference_percentage = 0

        budget_impact = (
            scenario_variance
            - baseline_variance
        )

        return {
            "project_name": project_name,

            "baseline": {
                "budget": baseline["budget"],

                "estimated_cost": baseline_cost,

                "variance": baseline_variance,

                "variance_percentage": baseline[
                    "summary"
                ]["variance_percentage"],

                "risk_level": baseline[
                    "summary"
                ]["risk_level"],

                "budget_status": baseline[
                    "summary"
                ]["budget_status"],
            },

            "scenario": {
                "budget": scenario["budget"],

                "estimated_cost": scenario_cost,

                "variance": scenario_variance,

                "variance_percentage": scenario[
                    "summary"
                ]["variance_percentage"],

                "risk_level": scenario[
                    "summary"
                ]["risk_level"],

                "budget_status": scenario[
                    "summary"
                ]["budget_status"],
            },

            "impact": {
                "cost_difference": round(
                    cost_difference,
                    2,
                ),

                "cost_difference_percentage": round(
                    cost_difference_percentage,
                    2,
                ),

                "budget_impact": round(
                    budget_impact,
                    2,
                ),

                "direction": direction,
            },

            "modified_items": scenario[
                "items"
            ],
        }

    # ---------------------------------------------------------
    # RISK CLASSIFICATION
    # ---------------------------------------------------------

    @classmethod
    def _risk_level(
        cls,
        variance_percentage: float,
    ) -> str:

        if variance_percentage <= cls.LOW_VARIANCE:
            return "LOW"

        if variance_percentage <= cls.MEDIUM_VARIANCE:
            return "MEDIUM"

        return "HIGH"

    # ---------------------------------------------------------
    # BUDGET STATUS
    # ---------------------------------------------------------

    @classmethod
    def _budget_status(
        cls,
        variance_percentage: float,
    ) -> str:

        if variance_percentage <= 0:
            return "WITHIN_BUDGET"

        if variance_percentage <= cls.LOW_VARIANCE:
            return "SLIGHTLY_OVER_BUDGET"

        if variance_percentage <= cls.MEDIUM_VARIANCE:
            return "AT_RISK"

        return "OVER_BUDGET"

    # ---------------------------------------------------------
    # RECOMMENDATION
    # ---------------------------------------------------------

    @staticmethod
    def _recommendation(
        variance_percentage: float,
    ) -> str:

        if variance_percentage <= 0:
            return (
                "Estimated project cost is within "
                "the approved budget."
            )

        if variance_percentage <= 5:
            return (
                "Cost is slightly above budget. "
                "Review procurement and installation costs."
            )

        if variance_percentage <= 10:
            return (
                "Project is at budget risk. "
                "Review high-cost items and "
                "contingency assumptions."
            )

        return (
            "Project is significantly over budget. "
            "Consider cost optimization, scope review, "
            "or budget revision."
        )