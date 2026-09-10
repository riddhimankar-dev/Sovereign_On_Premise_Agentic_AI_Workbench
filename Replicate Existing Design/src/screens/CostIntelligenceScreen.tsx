import { useEffect, useRef, useState } from "react";
import {
  Plus,
  Trash2,
  Calculator,
  RotateCcw,
  Play,
  Loader2,
  Save,
  Info,
  ChevronDown,
} from "lucide-react";

import CostSummary from "../components/CostSummary";
import CostBreakdown from "../components/CostBreakdown";
import WhatIfAnalysis from "../components/WhatIfAnalysis";

import { api } from "../services/api";
import type {
  CostEstimateResponse,
  CostItem,
  WhatIfResponse,
} from "../services/api";

const DEFAULT_ITEMS: CostItem[] = [
  {
    name: "Centrifugal Pump",
    category: "Equipment",
    material: "Stainless Steel",
    quantity: 2,
    unit_cost: 250000,
    installation_cost: 30000,
    maintenance_cost: 15000,
    criticality: "high",
    safety_critical: true,
  },
  {
    name: "Control Valve",
    category: "Instrumentation",
    material: "Carbon Steel",
    quantity: 4,
    unit_cost: 50000,
    installation_cost: 5000,
    maintenance_cost: 3000,
    criticality: "medium",
    safety_critical: false,
  },
];

const EMPTY_ITEM: CostItem = {
  name: "",
  category: "Equipment",
  material: "Carbon Steel",
  quantity: 1,
  unit_cost: 0,
  installation_cost: 0,
  maintenance_cost: 0,
  criticality: "low",
  safety_critical: false,
};

function toNumber(value: unknown): number {
  const numberValue = Number(value);

  return Number.isFinite(numberValue) ? numberValue : 0;
}

function unwrapResponse(response: unknown): any {
  const data = response as any;

  if (data?.result) {
    return data.result;
  }

  if (data?.data) {
    return data.data;
  }

  return data;
}

function getTotalCost(response: unknown): number {
  const data = unwrapResponse(response);

  const summary = data?.summary;

  const directTotal = toNumber(
    summary?.total_cost ??
      summary?.total_estimated_cost
  );

  if (directTotal > 0) {
    return directTotal;
  }

  if (Array.isArray(data?.items)) {
    const itemTotal = data.items.reduce(
      (sum: number, item: any) => {
        const itemTotalCost = toNumber(
          item?.total_cost
        );

        if (itemTotalCost > 0) {
          return sum + itemTotalCost;
        }

        const equipmentCost =
          toNumber(item?.equipment_cost);

        const installationCost =
          toNumber(item?.installation_cost);

        const maintenanceCost =
          toNumber(item?.maintenance_cost);

        const contingency = toNumber(
          item?.contingency ??
            item?.contingency_cost
        );

        return (
          sum +
          equipmentCost +
          installationCost +
          maintenanceCost +
          contingency
        );
      },
      0
    );

    if (itemTotal > 0) {
      return itemTotal;
    }
  }

  return 0;
}

function normalizeCostResponse(
  response: unknown
): CostEstimateResponse {
  const normalized = unwrapResponse(response);

  if (!normalized) {
    throw new Error(
      "Cost Engine returned an empty response."
    );
  }

  if (!normalized.summary) {
    throw new Error(
      "Cost Engine response does not contain a summary."
    );
  }

  if (!Array.isArray(normalized.items)) {
    throw new Error(
      "Cost Engine response does not contain engineering items."
    );
  }

  const summary = normalized.summary;

  const normalizedItems = normalized.items.map(
    (item: any) => {
      const quantity = toNumber(
        item.quantity
      );

      const unitCost = toNumber(
        item.unit_cost
      );

      const installationUnitCost =
        toNumber(
          item.installation_unit_cost ??
            item.installation_cost
        );

      const maintenanceUnitCost =
        toNumber(
          item.maintenance_unit_cost ??
            item.maintenance_cost
        );

      const equipmentCost = toNumber(
        item.equipment_cost ??
          quantity * unitCost
      );

      const installationCost = toNumber(
        item.installation_cost ??
          item.installation_total ??
          quantity *
            installationUnitCost
      );

      const maintenanceCost = toNumber(
        item.maintenance_cost ??
          item.maintenance_total ??
          quantity *
            maintenanceUnitCost
      );

      const baseCost = toNumber(
        item.base_cost ??
          equipmentCost +
            installationCost +
            maintenanceCost
      );

      const contingencyRate = toNumber(
        item.contingency_rate
      );

      const contingency = toNumber(
        item.contingency ??
          item.contingency_cost ??
          baseCost *
            (contingencyRate / 100)
      );

      const totalCost = toNumber(
        item.total_cost ??
          baseCost +
            contingency
      );

      return {
        ...item,
        quantity,
        unit_cost: unitCost,
        installation_unit_cost:
          installationUnitCost,
        maintenance_unit_cost:
          maintenanceUnitCost,
        equipment_cost:
          equipmentCost,
        installation_cost:
          installationCost,
        maintenance_cost:
          maintenanceCost,
        base_cost:
          baseCost,
        contingency_rate:
          contingencyRate,
        contingency,
        total_cost:
          totalCost,
      };
    }
  );

  const calculatedEquipmentCost =
    normalizedItems.reduce(
      (
        sum: number,
        item: any
      ) =>
        sum +
        toNumber(
          item.equipment_cost
        ),
      0
    );

  const calculatedInstallationCost =
    normalizedItems.reduce(
      (
        sum: number,
        item: any
      ) =>
        sum +
        toNumber(
          item.installation_cost
        ),
      0
    );

  const calculatedMaintenanceCost =
    normalizedItems.reduce(
      (
        sum: number,
        item: any
      ) =>
        sum +
        toNumber(
          item.maintenance_cost
        ),
      0
    );

  const calculatedBaseCost =
    normalizedItems.reduce(
      (
        sum: number,
        item: any
      ) =>
        sum +
        toNumber(
          item.base_cost
        ),
      0
    );

  const calculatedContingency =
    normalizedItems.reduce(
      (
        sum: number,
        item: any
      ) =>
        sum +
        toNumber(
          item.contingency
        ),
      0
    );

  const calculatedTotalCost =
    normalizedItems.reduce(
      (
        sum: number,
        item: any
      ) =>
        sum +
        toNumber(
          item.total_cost
        ),
      0
    );

  const budget = toNumber(
    normalized.budget ??
      summary.budget
  );

  const backendTotalCost =
    toNumber(
      summary.total_estimated_cost ??
        summary.total_cost
    );

  const totalCost =
    backendTotalCost > 0
      ? backendTotalCost
      : calculatedTotalCost;

  const backendVariance =
    toNumber(
      summary.variance
    );

  const variance =
    Number.isFinite(
      backendVariance
    ) &&
    (
      backendVariance !== 0 ||
      totalCost === budget
    )
      ? backendVariance
      : totalCost - budget;

  const backendVariancePercent =
    toNumber(
      summary.variance_percentage ??
        summary.variance_percent
    );

  const variancePercent =
    Number.isFinite(
      backendVariancePercent
    ) &&
    (
      backendVariancePercent !== 0 ||
      variance === 0
    )
      ? backendVariancePercent
      : budget > 0
      ? (variance / budget) * 100
      : 0;

  return {
    ...normalized,

    project_name:
      normalized.project_name || "",

    budget,

    items:
      normalizedItems,

    summary: {
      ...summary,

      equipment_cost:
        toNumber(
          summary.equipment_cost
        ) ||
        calculatedEquipmentCost,

      installation_cost:
        toNumber(
          summary.installation_cost
        ) ||
        calculatedInstallationCost,

      maintenance_cost:
        toNumber(
          summary.maintenance_cost
        ) ||
        calculatedMaintenanceCost,

      base_cost:
        toNumber(
          summary.base_cost
        ) ||
        calculatedBaseCost,

      contingency:
        toNumber(
          summary.contingency ??
            summary.contingency_cost
        ) ||
        calculatedContingency,

      contingency_cost:
        toNumber(
          summary.contingency ??
            summary.contingency_cost
        ) ||
        calculatedContingency,

      total_estimated_cost:
        totalCost,

      total_cost:
        totalCost,

      budget,

      variance,

      variance_percentage:
        variancePercent,

      variance_percent:
        variancePercent,

      risk_level:
        summary.risk_level ||
        "UNKNOWN",

      budget_status:
        summary.budget_status ||
        "UNKNOWN",

      recommendation:
        summary.recommendation ||
        "",
    },

    calculation_trace:
      normalized.calculation_trace ||
      {},
  } as CostEstimateResponse;
}

export default function CostIntelligenceScreen() {
  const [projectName, setProjectName] =
    useState(
      "Refinery Pump Upgrade"
    );

  const [budget, setBudget] =
    useState(1000000);

  const [items, setItems] =
    useState<CostItem[]>(
      DEFAULT_ITEMS.map(
        (item) => ({
          ...item,
        })
      )
    );

  const [estimate, setEstimate] =
    useState<CostEstimateResponse | null>(
      null
    );

  const [whatIfResult, setWhatIfResult] =
    useState<WhatIfResponse | null>(
      null
    );

  /*
   * INDEX OF ITEM SELECTED
   * FOR WHAT-IF ANALYSIS
   */
  const [
    selectedWhatIfIndex,
    setSelectedWhatIfIndex,
  ] = useState(0);

  /*
   * SCENARIO QUANTITY
   */
  const [
    scenarioQuantity,
    setScenarioQuantity,
  ] = useState(3);

  const [
    loadingEstimate,
    setLoadingEstimate,
  ] = useState(false);

  const [
    loadingWhatIf,
    setLoadingWhatIf,
  ] = useState(false);

  const [error, setError] =
    useState("");

  /*
   * --------------------------------------------------
   * NEW ITEM AUTO-FOCUS
   * --------------------------------------------------
   *
   * When a new engineering item is added,
   * this ref is used to automatically focus
   * its Item Name input.
   *
   * Therefore:
   *
   * Add Item
   *      ↓
   * New row appears
   *      ↓
   * Cursor automatically goes to Item Name
   *      ↓
   * Type the name immediately
   */
  const itemNameInputRefs =
    useRef<
      Array<HTMLInputElement | null>
    >([]);

  const [
    newlyAddedItemIndex,
    setNewlyAddedItemIndex,
  ] = useState<number | null>(null);

  useEffect(() => {
    if (
      newlyAddedItemIndex !== null &&
      itemNameInputRefs.current[
        newlyAddedItemIndex
      ]
    ) {
      itemNameInputRefs.current[
        newlyAddedItemIndex
      ]?.focus();

      itemNameInputRefs.current[
        newlyAddedItemIndex
      ]?.select();

      setNewlyAddedItemIndex(null);
    }
  }, [
    newlyAddedItemIndex,
    items.length,
  ]);

  /*
   * Currently selected What-If item.
   */
  const selectedWhatIfItem =
    items[selectedWhatIfIndex];

  /*
   * Update engineering item.
   */
  const updateItem = (
    index: number,
    updates: Partial<CostItem>
  ) => {
    setItems(
      (current) =>
        current.map(
          (
            item,
            itemIndex
          ) =>
            itemIndex === index
              ? {
                  ...item,
                  ...updates,
                }
              : item
        )
    );

    setEstimate(null);
    setWhatIfResult(null);
    setError("");

    /*
     * If the selected What-If item quantity
     * changes, keep scenario quantity sensible.
     */
    if (
      index ===
        selectedWhatIfIndex &&
      updates.quantity !== undefined
    ) {
      setScenarioQuantity(
        Math.max(
          1,
          toNumber(
            updates.quantity
          ) + 1
        )
      );
    }
  };

  /*
   * --------------------------------------------------
   * ADD ENGINEERING ITEM
   * --------------------------------------------------
   *
   * New item is created with a BLANK NAME.
   *
   * The name input is automatically focused
   * after the row is rendered.
   *
   * User does NOT need to click the block again.
   */
  const addItem = () => {
    const newIndex = items.length;

    const newItem: CostItem = {
      ...EMPTY_ITEM,
    };

    setItems(
      (current) => [
        ...current,
        newItem,
      ]
    );

    /*
     * Automatically select the newly
     * added item for What-If.
     */
    setSelectedWhatIfIndex(
      newIndex
    );

    setScenarioQuantity(
      newItem.quantity + 1
    );

    /*
     * Tell useEffect to focus
     * the newly added name input.
     */
    setNewlyAddedItemIndex(
      newIndex
    );

    setEstimate(null);
    setWhatIfResult(null);
    setError("");
  };

  /*
   * Remove engineering item.
   */
  const removeItem = (
    index: number
  ) => {
    if (items.length <= 1) {
      return;
    }

    setItems(
      (current) =>
        current.filter(
          (
            _,
            itemIndex
          ) =>
            itemIndex !== index
        )
    );

    /*
     * Keep What-If selection valid.
     */
    if (
      index ===
      selectedWhatIfIndex
    ) {
      const remainingItems =
        items.filter(
          (
            _,
            itemIndex
          ) =>
            itemIndex !== index
        );

      if (
        remainingItems.length === 0
      ) {
        setSelectedWhatIfIndex(0);
        setScenarioQuantity(1);
      } else {
        const nextIndex =
          Math.min(
            index,
            remainingItems.length - 1
          );

        setSelectedWhatIfIndex(
          nextIndex
        );

        setScenarioQuantity(
          Math.max(
            1,
            toNumber(
              remainingItems[
                nextIndex
              ]?.quantity
            ) + 1
          )
        );
      }
    } else if (
      index <
      selectedWhatIfIndex
    ) {
      setSelectedWhatIfIndex(
        (current) =>
          Math.max(
            0,
            current - 1
          )
      );
    }

    setEstimate(null);
    setWhatIfResult(null);
    setError("");
  };

  /*
   * Handle What-If item selection.
   */
  const handleWhatIfItemChange = (
    index: number
  ) => {
    setSelectedWhatIfIndex(
      index
    );

    const selectedItem =
      items[index];

    setScenarioQuantity(
      Math.max(
        1,
        toNumber(
          selectedItem?.quantity
        ) + 1
      )
    );

    setWhatIfResult(null);
    setError("");
  };

  /*
   * REAL BACKEND COST CALCULATION
   */
  const calculateEstimate =
    async () => {
      if (!projectName.trim()) {
        setError(
          "Please enter a project name."
        );
        return;
      }

      if (
        !Number.isFinite(budget) ||
        budget <= 0
      ) {
        setError(
          "Project budget must be greater than zero."
        );
        return;
      }

      if (items.length === 0) {
        setError(
          "Add at least one engineering item first."
        );
        return;
      }

      /*
       * Do not allow unnamed engineering items
       * to be submitted to the backend.
       */
      const unnamedItem =
        items.findIndex(
          (item) =>
            !item.name?.trim()
        );

      if (
        unnamedItem !== -1
      ) {
        setError(
          `Please enter a name for Engineering Item ${unnamedItem + 1}.`
        );

        setNewlyAddedItemIndex(
          unnamedItem
        );

        return;
      }

      setError("");
      setWhatIfResult(null);
      setLoadingEstimate(true);

      try {
        console.log(
          "Sending cost calculation to backend:",
          {
            project_name:
              projectName,
            budget,
            items,
          }
        );

        const response =
          await api.cost.estimate({
            project_name:
              projectName,
            budget,
            items,
          });

        console.log(
          "Cost Engine response:",
          response
        );

        const result =
          normalizeCostResponse(
            response
          );

        console.log(
          "Normalized cost result:",
          result
        );

        setEstimate(result);

        /*
         * Keep the currently selected What-If item
         * if it is still valid.
         *
         * If not, select the first item.
         */
        const validIndex =
          selectedWhatIfIndex >= 0 &&
          selectedWhatIfIndex <
            items.length
            ? selectedWhatIfIndex
            : 0;

        setSelectedWhatIfIndex(
          validIndex
        );

        setScenarioQuantity(
          Math.max(
            1,
            toNumber(
              items[
                validIndex
              ].quantity
            ) + 1
          )
        );
      } catch (err) {
        console.error(
          "Cost calculation failed:",
          err
        );

        setEstimate(null);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to calculate project cost."
        );
      } finally {
        setLoadingEstimate(false);
      }
    };

  /*
   * REAL BACKEND WHAT-IF CALCULATION
   *
   * Uses /cost/estimate twice:
   *
   * 1. Baseline = current items
   * 2. Scenario = selected item's quantity changed
   */
  const runWhatIf =
    async () => {
      if (items.length === 0) {
        setError(
          "Add at least one engineering item first."
        );
        return;
      }

      if (
        selectedWhatIfIndex < 0 ||
        selectedWhatIfIndex >=
          items.length
      ) {
        setError(
          "Please select a valid engineering item."
        );
        return;
      }

      /*
       * Make sure no item is unnamed.
       */
      const unnamedItem =
        items.findIndex(
          (item) =>
            !item.name?.trim()
        );

      if (
        unnamedItem !== -1
      ) {
        setError(
          `Please enter a name for Engineering Item ${unnamedItem + 1} before running What-If.`
        );

        setNewlyAddedItemIndex(
          unnamedItem
        );

        return;
      }

      if (
        !Number.isFinite(
          scenarioQuantity
        ) ||
        scenarioQuantity <= 0
      ) {
        setError(
          "Scenario quantity must be greater than zero."
        );
        return;
      }

      if (
        !projectName.trim() ||
        !Number.isFinite(budget) ||
        budget <= 0
      ) {
        setError(
          "Please provide a valid project name and budget."
        );
        return;
      }

      setError("");
      setLoadingWhatIf(true);

      try {
        /*
         * ---------------------------------------------
         * STEP 1
         * BASELINE
         * ---------------------------------------------
         */
        const baselineRequest = {
          project_name:
            projectName,
          budget,
          items:
            items.map(
              (item) => ({
                ...item,
              })
            ),
        };

        console.log(
          "WHAT-IF BASELINE REQUEST:",
          baselineRequest
        );

        const baselineResponse =
          await api.cost.estimate(
            baselineRequest
          );

        console.log(
          "WHAT-IF BASELINE RAW RESPONSE:",
          baselineResponse
        );

        const baseline =
          normalizeCostResponse(
            baselineResponse
          );

        console.log(
          "WHAT-IF BASELINE NORMALIZED:",
          baseline
        );

        /*
         * ---------------------------------------------
         * STEP 2
         * SCENARIO
         *
         * ONLY THE SELECTED ITEM CHANGES.
         * ---------------------------------------------
         */
        const scenarioItems =
          items.map(
            (
              item,
              index
            ) => {
              if (
                index ===
                selectedWhatIfIndex
              ) {
                return {
                  ...item,
                  quantity:
                    scenarioQuantity,
                };
              }

              return {
                ...item,
              };
            }
          );

        const scenarioRequest = {
          project_name:
            projectName,
          budget,
          items:
            scenarioItems,
        };

        console.log(
          "WHAT-IF SCENARIO REQUEST:",
          scenarioRequest
        );

        /*
         * ---------------------------------------------
         * STEP 3
         * SCENARIO BACKEND CALCULATION
         * ---------------------------------------------
         */
        const scenarioResponse =
          await api.cost.estimate(
            scenarioRequest
          );

        console.log(
          "WHAT-IF SCENARIO RAW RESPONSE:",
          scenarioResponse
        );

        const scenario =
          normalizeCostResponse(
            scenarioResponse
          );

        console.log(
          "WHAT-IF SCENARIO NORMALIZED:",
          scenario
        );

        /*
         * ---------------------------------------------
         * STEP 4
         * TOTALS
         * ---------------------------------------------
         */
        const baselineTotal =
          getTotalCost(
            baseline
          );

        const scenarioTotal =
          getTotalCost(
            scenario
          );

        /*
         * ---------------------------------------------
         * STEP 5
         * COST IMPACT
         * ---------------------------------------------
         */
        const totalCostChange =
          scenarioTotal -
          baselineTotal;

        const totalCostChangePercent =
          baselineTotal > 0
            ? (
                totalCostChange /
                baselineTotal
              ) *
              100
            : 0;

        /*
         * ---------------------------------------------
         * STEP 6
         * BUDGET CHANGE
         * ---------------------------------------------
         */
        const budgetChange =
          toNumber(
            scenario.budget
          ) -
          toNumber(
            baseline.budget
          );

        /*
         * ---------------------------------------------
         * STEP 7
         * RISK
         * ---------------------------------------------
         */
        const baselineRisk =
          baseline.summary
            ?.risk_level ||
          "UNKNOWN";

        const scenarioRisk =
          scenario.summary
            ?.risk_level ||
          "UNKNOWN";

        /*
         * ---------------------------------------------
         * STEP 8
         * BUDGET STATUS
         * ---------------------------------------------
         */
        const baselineStatus =
          baseline.summary
            ?.budget_status ||
          "UNKNOWN";

        const scenarioStatus =
          scenario.summary
            ?.budget_status ||
          "UNKNOWN";

        /*
         * ---------------------------------------------
         * STEP 9
         * FINAL RESULT
         * ---------------------------------------------
         */
        const result =
          {
            engine_version:
              scenario.engine_version ||
              baseline.engine_version ||
              "1.0",

            project_name:
              projectName,

            baseline:
              baseline,

            scenario:
              scenario,

            comparison: {
              total_cost_change:
                totalCostChange,

              total_cost_change_percent:
                totalCostChangePercent,

              budget_change:
                budgetChange,

              risk_change:
                `${baselineRisk} → ${scenarioRisk}`,

              budget_status_change:
                `${baselineStatus} → ${scenarioStatus}`,
            },
          } as WhatIfResponse;

        console.log(
          "======================================"
        );

        console.log(
          "WHAT-IF FINAL RESULT"
        );

        console.log(
          "Selected Item:",
          selectedWhatIfItem?.name
        );

        console.log(
          "Current Quantity:",
          selectedWhatIfItem?.quantity
        );

        console.log(
          "Scenario Quantity:",
          scenarioQuantity
        );

        console.log(
          "Baseline:",
          baselineTotal
        );

        console.log(
          "Scenario:",
          scenarioTotal
        );

        console.log(
          "Change:",
          totalCostChange
        );

        console.log(
          "Change %:",
          totalCostChangePercent
        );

        console.log(
          "Risk:",
          `${baselineRisk} → ${scenarioRisk}`
        );

        console.log(
          "Budget Status:",
          `${baselineStatus} → ${scenarioStatus}`
        );

        console.log(
          "FINAL WHAT-IF RESULT:",
          result
        );

        console.log(
          "======================================"
        );

        setWhatIfResult(
          result
        );
      } catch (err) {
        console.error(
          "What-If calculation failed:",
          err
        );

        setWhatIfResult(null);

        setError(
          err instanceof Error
            ? err.message
            : "Unable to run What-If analysis."
        );
      } finally {
        setLoadingWhatIf(false);
      }
    };

  /*
   * Reset UI inputs.
   */
  const resetAll = () => {
    setProjectName(
      "Refinery Pump Upgrade"
    );

    setBudget(
      1000000
    );

    setItems(
      DEFAULT_ITEMS.map(
        (item) => ({
          ...item,
        })
      )
    );

    setSelectedWhatIfIndex(
      0
    );

    setScenarioQuantity(
      3
    );

    setEstimate(null);

    setWhatIfResult(null);

    setError("");

    setNewlyAddedItemIndex(
      null
    );

    itemNameInputRefs.current =
      [];
  };

  /*
   * Save backend calculation result.
   */
  const saveEstimate = () => {
    if (!estimate) {
      return;
    }

    const data =
      JSON.stringify(
        estimate,
        null,
        2
      );

    const blob =
      new Blob(
        [data],
        {
          type: "application/json",
        }
      );

    const url =
      URL.createObjectURL(
        blob
      );

    const anchor =
      document.createElement(
        "a"
      );

    anchor.href =
      url;

    anchor.download =
      `${projectName
        .replace(/\s+/g, "_")
        .toLowerCase()}_cost_estimate.json`;

    document.body.appendChild(
      anchor
    );

    anchor.click();

    document.body.removeChild(
      anchor
    );

    URL.revokeObjectURL(
      url
    );
  };

  return (
    <div className="h-full overflow-y-auto bg-[#080E19] text-[#F5F7FA]">

      {/* HEADER */}
      <div className="sticky top-0 z-20 border-b border-[#253248] bg-[#080E19]/95 backdrop-blur">
        <div className="px-6 py-4">

          <div className="flex items-start justify-between gap-6">

            <div className="flex items-start gap-3">

              <div className="w-10 h-10 rounded-lg bg-[#8B5CF6]/10 border border-[#8B5CF6]/20 flex items-center justify-center">
                <Calculator
                  size={19}
                  className="text-[#8B5CF6]"
                />
              </div>

              <div>

                <h1 className="text-[16px] font-semibold">
                  Engineering Cost Intelligence
                </h1>

                <p className="text-[10px] text-[#667386] mt-1">
                  Deterministic engineering cost
                  estimation, budget analysis and
                  What-If scenario planning
                </p>

              </div>

            </div>

            <div className="flex items-center gap-2">

              <button
                onClick={
                  resetAll
                }
                className="h-8 px-3 rounded-md border border-[#253248] bg-[#0F1726] text-[#9AA6B5] hover:text-[#F5F7FA] hover:bg-[#141E2F] transition-colors flex items-center gap-2 text-[10px]"
              >
                <RotateCcw size={12} />
                Reset
              </button>

              {estimate && (
                <button
                  onClick={
                    saveEstimate
                  }
                  className="h-8 px-3 rounded-md border border-[#253248] bg-[#0F1726] text-[#9AA6B5] hover:text-[#F5F7FA] hover:bg-[#141E2F] transition-colors flex items-center gap-2 text-[10px]"
                >
                  <Save size={12} />
                  Save Result
                </button>
              )}

            </div>

          </div>

        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="p-6 max-w-[1500px] mx-auto">

        {/* PROJECT CONFIGURATION */}
        <section className="rounded-lg border border-[#253248] bg-[#0F1726] mb-5">

          <div className="px-4 py-3 border-b border-[#253248] flex items-center gap-2">

            <div className="w-6 h-6 rounded bg-[#3B82F6]/10 flex items-center justify-center">
              <Info
                size={12}
                className="text-[#3B82F6]"
              />
            </div>

            <div>

              <h2 className="text-[11px] font-semibold">
                Project Configuration
              </h2>

              <p className="text-[9px] text-[#667386] mt-0.5">
                Define the project budget and
                engineering cost inputs
              </p>

            </div>

          </div>

          <div className="p-4 grid grid-cols-2 gap-4">

            {/* PROJECT NAME */}
            <div>

              <label className="block text-[9px] uppercase tracking-wide font-semibold text-[#667386] mb-1.5">
                Project Name
              </label>

              <input
                type="text"
                value={
                  projectName
                }
                onChange={(
                  event
                ) => {
                  setProjectName(
                    event.target.value
                  );

                  setEstimate(null);
                  setWhatIfResult(null);
                  setError("");
                }}
                className="w-full h-9 px-3 rounded-md border border-[#253248] bg-[#0A1220] text-[11px] text-[#F5F7FA] outline-none focus:border-[#8B5CF6]"
                placeholder="Enter project name"
              />

            </div>

            {/* BUDGET */}
            <div>

              <label className="block text-[9px] uppercase tracking-wide font-semibold text-[#667386] mb-1.5">
                Project Budget
              </label>

              <div className="relative">

                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[11px] text-[#667386]">
                  ₹
                </span>

                <input
                  type="number"
                  min={1}
                  value={
                    budget
                  }
                  onChange={(
                    event
                  ) => {
                    setBudget(
                      Math.max(
                        0,
                        Number(
                          event.target.value
                        )
                      )
                    );

                    setEstimate(null);
                    setWhatIfResult(null);
                    setError("");
                  }}
                  className="w-full h-9 pl-7 pr-3 rounded-md border border-[#253248] bg-[#0A1220] text-[11px] text-[#F5F7FA] font-mono outline-none focus:border-[#8B5CF6]"
                />

              </div>

            </div>

          </div>

        </section>

        {/* ENGINEERING ITEMS */}
        <section className="rounded-lg border border-[#253248] bg-[#0F1726] mb-5">

          <div className="px-4 py-3 border-b border-[#253248] flex items-center justify-between">

            <div>

              <h2 className="text-[11px] font-semibold">
                Engineering Cost Items
              </h2>

              <p className="text-[9px] text-[#667386] mt-0.5">
                Equipment, installation,
                maintenance and risk parameters
              </p>

            </div>

            <button
              onClick={
                addItem
              }
              className="h-8 px-3 rounded-md bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-[10px] font-medium flex items-center gap-2 transition-colors"
            >
              <Plus size={12} />
              Add Item
            </button>

          </div>

          <div className="overflow-x-auto">

            <table className="w-full min-w-[1100px]">

              <thead>

                <tr className="border-b border-[#253248] bg-[#0A1220]">

                  <th className="text-left px-4 py-3 text-[8px] uppercase tracking-wide text-[#667386] font-semibold">
                    Engineering Item
                  </th>

                  <th className="text-left px-3 py-3 text-[8px] uppercase tracking-wide text-[#667386] font-semibold">
                    Category
                  </th>

                  <th className="text-left px-3 py-3 text-[8px] uppercase tracking-wide text-[#667386] font-semibold">
                    Material
                  </th>

                  <th className="text-left px-3 py-3 text-[8px] uppercase tracking-wide text-[#667386] font-semibold">
                    Qty
                  </th>

                  <th className="text-left px-3 py-3 text-[8px] uppercase tracking-wide text-[#667386] font-semibold">
                    Unit Cost
                  </th>

                  <th className="text-left px-3 py-3 text-[8px] uppercase tracking-wide text-[#667386] font-semibold">
                    Installation
                  </th>

                  <th className="text-left px-3 py-3 text-[8px] uppercase tracking-wide text-[#667386] font-semibold">
                    Maintenance
                  </th>

                  <th className="text-left px-3 py-3 text-[8px] uppercase tracking-wide text-[#667386] font-semibold">
                    Criticality
                  </th>

                  <th className="text-left px-3 py-3 text-[8px] uppercase tracking-wide text-[#667386] font-semibold">
                    Safety
                  </th>

                  <th className="w-10 px-3 py-3"></th>

                </tr>

              </thead>

              <tbody>

                {items.map(
                  (
                    item,
                    index
                  ) => (

                    <tr
                      key={index}
                      className={`border-b border-[#253248] last:border-b-0 ${
                        index ===
                        newlyAddedItemIndex
                          ? "bg-[#8B5CF6]/5"
                          : ""
                      }`}
                    >

                      {/* NAME */}
                      <td className="px-4 py-3">

                        <input
                          ref={(element) => {
                            itemNameInputRefs.current[
                              index
                            ] = element;
                          }}
                          type="text"
                          value={
                            item.name
                          }
                          onChange={(
                            event
                          ) =>
                            updateItem(
                              index,
                              {
                                name:
                                  event.target.value,
                              }
                            )
                          }
                          className={`w-[180px] h-8 px-2.5 rounded border bg-[#0A1220] text-[10px] text-[#F5F7FA] outline-none focus:border-[#8B5CF6] ${
                            index ===
                            newlyAddedItemIndex
                              ? "border-[#8B5CF6]"
                              : "border-[#253248]"
                          }`}
                          placeholder="Type item name..."
                        />

                      </td>

                      {/* CATEGORY */}
                      <td className="px-3 py-3">

                        <input
                          type="text"
                          value={
                            item.category ??
                            ""
                          }
                          onChange={(
                            event
                          ) =>
                            updateItem(
                              index,
                              {
                                category:
                                  event.target.value,
                              }
                            )
                          }
                          className="w-[120px] h-8 px-2.5 rounded border border-[#253248] bg-[#0A1220] text-[10px] text-[#F5F7FA] outline-none focus:border-[#8B5CF6]"
                          placeholder="Category"
                        />

                      </td>

                      {/* MATERIAL */}
                      <td className="px-3 py-3">

                        <input
                          type="text"
                          value={
                            item.material ??
                            ""
                          }
                          onChange={(
                            event
                          ) =>
                            updateItem(
                              index,
                              {
                                material:
                                  event.target.value,
                              }
                            )
                          }
                          className="w-[130px] h-8 px-2.5 rounded border border-[#253248] bg-[#0A1220] text-[10px] text-[#F5F7FA] outline-none focus:border-[#8B5CF6]"
                          placeholder="Material"
                        />

                      </td>

                      {/* QUANTITY */}
                      <td className="px-3 py-3">

                        <input
                          type="number"
                          min={1}
                          step={1}
                          value={
                            item.quantity
                          }
                          onChange={(
                            event
                          ) =>
                            updateItem(
                              index,
                              {
                                quantity:
                                  Math.max(
                                    1,
                                    Number(
                                      event.target.value
                                    )
                                  ),
                              }
                            )
                          }
                          className="w-[70px] h-8 px-2 rounded border border-[#253248] bg-[#0A1220] text-[10px] text-[#F5F7FA] font-mono outline-none focus:border-[#8B5CF6]"
                        />

                      </td>

                      {/* UNIT COST */}
                      <td className="px-3 py-3">

                        <input
                          type="number"
                          min={0}
                          value={
                            item.unit_cost
                          }
                          onChange={(
                            event
                          ) =>
                            updateItem(
                              index,
                              {
                                unit_cost:
                                  Math.max(
                                    0,
                                    Number(
                                      event.target.value
                                    )
                                  ),
                              }
                            )
                          }
                          className="w-[105px] h-8 px-2 rounded border border-[#253248] bg-[#0A1220] text-[10px] text-[#F5F7FA] font-mono outline-none focus:border-[#8B5CF6]"
                        />

                      </td>

                      {/* INSTALLATION */}
                      <td className="px-3 py-3">

                        <input
                          type="number"
                          min={0}
                          value={
                            item.installation_cost
                          }
                          onChange={(
                            event
                          ) =>
                            updateItem(
                              index,
                              {
                                installation_cost:
                                  Math.max(
                                    0,
                                    Number(
                                      event.target.value
                                    )
                                  ),
                              }
                            )
                          }
                          className="w-[105px] h-8 px-2 rounded border border-[#253248] bg-[#0A1220] text-[10px] text-[#F5F7FA] font-mono outline-none focus:border-[#8B5CF6]"
                        />

                      </td>

                      {/* MAINTENANCE */}
                      <td className="px-3 py-3">

                        <input
                          type="number"
                          min={0}
                          value={
                            item.maintenance_cost
                          }
                          onChange={(
                            event
                          ) =>
                            updateItem(
                              index,
                              {
                                maintenance_cost:
                                  Math.max(
                                    0,
                                    Number(
                                      event.target.value
                                    )
                                  ),
                              }
                            )
                          }
                          className="w-[105px] h-8 px-2 rounded border border-[#253248] bg-[#0A1220] text-[10px] text-[#F5F7FA] font-mono outline-none focus:border-[#8B5CF6]"
                        />

                      </td>

                      {/* CRITICALITY */}
                      <td className="px-3 py-3">

                        <div className="relative w-[100px]">

                          <select
                            value={
                              item.criticality
                            }
                            onChange={(
                              event
                            ) =>
                              updateItem(
                                index,
                                {
                                  criticality:
                                    event.target.value,
                                }
                              )
                            }
                            className="appearance-none w-full h-8 px-2 pr-6 rounded border border-[#253248] bg-[#0A1220] text-[10px] text-[#F5F7FA] outline-none focus:border-[#8B5CF6]"
                          >

                            <option value="low">
                              Low
                            </option>

                            <option value="medium">
                              Medium
                            </option>

                            <option value="high">
                              High
                            </option>

                            <option value="critical">
                              Critical
                            </option>

                          </select>

                          <ChevronDown
                            size={11}
                            className="absolute right-2 top-1/2 -translate-y-1/2 text-[#667386] pointer-events-none"
                          />

                        </div>

                      </td>

                      {/* SAFETY */}
                      <td className="px-3 py-3">

                        <button
                          onClick={() =>
                            updateItem(
                              index,
                              {
                                safety_critical:
                                  !item.safety_critical,
                              }
                            )
                          }
                          className={`w-8 h-8 rounded border flex items-center justify-center transition-colors ${
                            item.safety_critical
                              ? "border-[#EF4444]/30 bg-[#EF4444]/10 text-[#EF4444]"
                              : "border-[#253248] bg-[#0A1220] text-[#667386]"
                          }`}
                          title={
                            item.safety_critical
                              ? "Safety critical"
                              : "Not safety critical"
                          }
                        >
                          {item.safety_critical
                            ? "✓"
                            : "—"}
                        </button>

                      </td>

                      {/* DELETE */}
                      <td className="px-3 py-3">

                        <button
                          onClick={() =>
                            removeItem(
                              index
                            )
                          }
                          disabled={
                            items.length ===
                            1
                          }
                          className="w-7 h-7 rounded flex items-center justify-center text-[#667386] hover:text-[#EF4444] hover:bg-[#EF4444]/10 disabled:opacity-30 disabled:hover:bg-transparent disabled:hover:text-[#667386] transition-colors"
                          title="Remove item"
                        >
                          <Trash2
                            size={13}
                          />
                        </button>

                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

          {/* CALCULATE */}
          <div className="px-4 py-3 border-t border-[#253248] flex items-center justify-between">

            <div className="text-[9px] text-[#667386]">
              {items.length} engineering{" "}
              {items.length === 1
                ? "item"
                : "items"}{" "}
              configured
            </div>

            <button
              onClick={
                calculateEstimate
              }
              disabled={
                loadingEstimate ||
                items.length === 0
              }
              className="h-9 px-4 rounded-md bg-[#8B5CF6] hover:bg-[#7C3AED] disabled:opacity-50 disabled:cursor-not-allowed text-white text-[10px] font-semibold flex items-center gap-2 transition-colors"
            >

              {loadingEstimate ? (
                <>
                  <Loader2
                    size={13}
                    className="animate-spin"
                  />
                  Calculating...
                </>
              ) : (
                <>
                  <Calculator
                    size={13}
                  />
                  Calculate Cost
                </>
              )}

            </button>

          </div>

        </section>

        {/* ERROR */}
        {error && (
          <div className="mb-5 rounded-lg border border-[#EF4444]/30 bg-[#EF4444]/5 px-4 py-3 flex items-start gap-3">

            <div className="w-6 h-6 rounded bg-[#EF4444]/10 flex items-center justify-center shrink-0">
              <Info
                size={13}
                className="text-[#EF4444]"
              />
            </div>

            <div>

              <p className="text-[10px] font-semibold text-[#EF4444]">
                Cost Engine Error
              </p>

              <p className="text-[9px] text-[#9AA6B5] mt-1 leading-relaxed">
                {error}
              </p>

            </div>

          </div>
        )}

        {/* RESULTS */}
        {estimate && (
          <div className="space-y-5">

            {/* RESULT HEADER */}
            <div className="flex items-center justify-between">

              <div>

                <h2 className="text-[13px] font-semibold">
                  Cost Estimate
                </h2>

                <p className="text-[9px] text-[#667386] mt-1">
                  Backend calculation for{" "}
                  {estimate.project_name}
                </p>

              </div>

              <div className="flex items-center gap-2">

                <span className="px-2.5 py-1 rounded-md bg-[#14B8A6]/10 border border-[#14B8A6]/20 text-[#14B8A6] text-[8px] font-semibold uppercase">
                  Deterministic
                </span>

                <span className="px-2.5 py-1 rounded-md bg-[#253248] text-[#9AA6B5] text-[8px] font-mono">
                  Engine v
                  {estimate.engine_version}
                </span>

              </div>

            </div>

            {/* SUMMARY */}
            {estimate.summary && (
              <CostSummary
                totalCost={getTotalCost(
                  estimate
                )}
                budget={toNumber(
                  estimate.budget
                )}
                variance={toNumber(
                  estimate.summary
                    .variance
                )}
                variancePercent={toNumber(
                  estimate.summary
                    .variance_percent
                )}
                riskLevel={
                  estimate.summary
                    .risk_level ||
                  "UNKNOWN"
                }
                budgetStatus={
                  estimate.summary
                    .budget_status ||
                  "UNKNOWN"
                }
              />
            )}

            {/* BREAKDOWN */}
            {Array.isArray(
              estimate.items
            ) && (
              <CostBreakdown
                items={
                  estimate.items
                }
              />
            )}

            {/* RECOMMENDATION */}
            {estimate.summary
              ?.recommendation && (
              <div className="rounded-lg border border-[#253248] bg-[#0F1726] p-4">

                <div className="flex items-start gap-3">

                  <div className="w-7 h-7 rounded-md bg-[#3B82F6]/10 flex items-center justify-center shrink-0">

                    <Info
                      size={14}
                      className="text-[#3B82F6]"
                    />

                  </div>

                  <div>

                    <p className="text-[10px] uppercase tracking-wide font-semibold text-[#667386]">
                      Engineering Recommendation
                    </p>

                    <p className="text-[11px] text-[#D8DEE7] mt-1 leading-relaxed">
                      {
                        estimate
                          .summary
                          .recommendation
                      }
                    </p>

                  </div>

                </div>

              </div>
            )}

            {/* WHAT-IF */}
            <section className="rounded-lg border border-[#253248] bg-[#0F1726]">

              <div className="px-4 py-3 border-b border-[#253248]">

                <div className="flex items-center gap-2">

                  <div className="w-7 h-7 rounded-md bg-[#8B5CF6]/10 flex items-center justify-center">

                    <Play
                      size={13}
                      className="text-[#8B5CF6]"
                    />

                  </div>

                  <div>

                    <h2 className="text-[11px] font-semibold">
                      What-If Scenario
                    </h2>

                    <p className="text-[9px] text-[#667386] mt-0.5">
                      Test how changing any
                      engineering item affects
                      project cost
                    </p>

                  </div>

                </div>

              </div>

              <div className="p-4">

                <div className="flex items-end gap-4">

                  {/* ITEM SELECTOR */}
                  <div className="flex-1">

                    <label className="block text-[9px] uppercase tracking-wide font-semibold text-[#667386] mb-1.5">
                      Item
                    </label>

                    <div className="relative">

                      <select
                        value={
                          selectedWhatIfIndex
                        }
                        onChange={(
                          event
                        ) =>
                          handleWhatIfItemChange(
                            Number(
                              event.target.value
                            )
                          )
                        }
                        className="appearance-none w-full h-9 px-3 pr-8 rounded-md border border-[#253248] bg-[#0A1220] text-[10px] text-[#F5F7FA] outline-none focus:border-[#8B5CF6]"
                      >

                        {items.map(
                          (
                            item,
                            index
                          ) => (
                            <option
                              key={`${index}-${item.name}`}
                              value={index}
                            >
                              {item.name ||
                                `Engineering Item ${index + 1}`}
                            </option>
                          )
                        )}

                      </select>

                      <ChevronDown
                        size={12}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-[#667386] pointer-events-none"
                      />

                    </div>

                  </div>

                  {/* CURRENT QUANTITY */}
                  <div className="w-[140px]">

                    <label className="block text-[9px] uppercase tracking-wide font-semibold text-[#667386] mb-1.5">
                      Current Quantity
                    </label>

                    <div className="h-9 px-3 rounded-md border border-[#253248] bg-[#0A1220] flex items-center">

                      <span className="text-[10px] font-mono text-[#9AA6B5]">
                        {selectedWhatIfItem
                          ?.quantity ??
                          0}
                      </span>

                    </div>

                  </div>

                  {/* SCENARIO QUANTITY */}
                  <div className="w-[160px]">

                    <label className="block text-[9px] uppercase tracking-wide font-semibold text-[#667386] mb-1.5">
                      Scenario Quantity
                    </label>

                    <input
                      type="number"
                      min={1}
                      step={1}
                      value={
                        scenarioQuantity
                      }
                      onChange={(
                        event
                      ) =>
                        setScenarioQuantity(
                          Math.max(
                            1,
                            Number(
                              event.target.value
                            )
                          )
                        )
                      }
                      className="w-full h-9 px-3 rounded-md border border-[#253248] bg-[#0A1220] text-[10px] font-mono text-[#F5F7FA] outline-none focus:border-[#8B5CF6]"
                    />

                  </div>

                  {/* RUN */}
                  <button
                    onClick={
                      runWhatIf
                    }
                    disabled={
                      loadingWhatIf ||
                      items.length === 0
                    }
                    className="h-9 px-4 rounded-md bg-[#8B5CF6] hover:bg-[#7C3AED] disabled:opacity-50 disabled:cursor-not-allowed text-white text-[10px] font-semibold flex items-center gap-2 transition-colors"
                  >

                    {loadingWhatIf ? (
                      <>
                        <Loader2
                          size={13}
                          className="animate-spin"
                        />
                        Running...
                      </>
                    ) : (
                      <>
                        <Play
                          size={12}
                        />
                        Run What-If
                      </>
                    )}

                  </button>

                </div>

                {/* DYNAMIC EXAMPLE */}
                <div className="mt-3 px-3 py-2 rounded-md bg-[#141E2F] border border-[#253248]">

                  <p className="text-[9px] text-[#667386]">

                    Example: change{" "}

                    <span className="text-[#F5F7FA] font-semibold">

                      {selectedWhatIfItem
                        ?.quantity ??
                        0}{" "}

                      {selectedWhatIfItem
                        ?.name ||
                        "item"}{" "}

                      →{" "}

                      {scenarioQuantity}{" "}

                      {selectedWhatIfItem
                        ?.name ||
                        "item"}

                    </span>{" "}

                    to evaluate the resulting
                    project cost, variance and
                    risk.

                  </p>

                </div>

              </div>

            </section>

            {/* WHAT-IF RESULT */}
            {whatIfResult && (
              <WhatIfAnalysis
                baselineCost={getTotalCost(
                  whatIfResult.baseline
                )}

                scenarioCost={getTotalCost(
                  whatIfResult.scenario
                )}

                change={toNumber(
                  whatIfResult
                    .comparison
                    ?.total_cost_change
                )}

                changePercent={toNumber(
                  whatIfResult
                    .comparison
                    ?.total_cost_change_percent
                )}

                riskChange={
                  whatIfResult
                    .comparison
                    ?.risk_change ||
                  `${
                    whatIfResult
                      .baseline
                      ?.summary
                      ?.risk_level ||
                    "UNKNOWN"
                  } → ${
                    whatIfResult
                      .scenario
                      ?.summary
                      ?.risk_level ||
                    "UNKNOWN"
                  }`
                }

                statusChange={
                  whatIfResult
                    .comparison
                    ?.budget_status_change ||
                  `${
                    whatIfResult
                      .baseline
                      ?.summary
                      ?.budget_status ||
                    "UNKNOWN"
                  } → ${
                    whatIfResult
                      .scenario
                      ?.summary
                      ?.budget_status ||
                    "UNKNOWN"
                  }`
                }
              />
            )}

          </div>
        )}

        {/* EMPTY STATE */}
        {!estimate &&
          !loadingEstimate &&
          !error && (
            <div className="rounded-lg border border-dashed border-[#253248] bg-[#0F1726] p-10 flex flex-col items-center justify-center text-center">

              <div className="w-12 h-12 rounded-xl bg-[#8B5CF6]/10 border border-[#8B5CF6]/20 flex items-center justify-center mb-4">

                <Calculator
                  size={22}
                  className="text-[#8B5CF6]"
                />

              </div>

              <h3 className="text-[13px] font-semibold">
                Ready for Cost Analysis
              </h3>

              <p className="max-w-[500px] text-[10px] text-[#667386] mt-2 leading-relaxed">
                Configure your project budget
                and engineering items above,
                then run the deterministic
                backend cost engine to calculate
                equipment, installation,
                maintenance, contingency and
                budget risk.
              </p>

              <button
                onClick={
                  calculateEstimate
                }
                disabled={
                  items.length === 0
                }
                className="mt-5 h-9 px-4 rounded-md bg-[#8B5CF6] hover:bg-[#7C3AED] disabled:opacity-50 text-white text-[10px] font-semibold flex items-center gap-2 transition-colors"
              >
                <Calculator
                  size={13}
                />
                Calculate Initial Estimate
              </button>

            </div>
          )}

      </div>
    </div>
  );
}