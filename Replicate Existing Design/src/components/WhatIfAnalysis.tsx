import {
  ArrowRight,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  GitCompare,
} from "lucide-react";

interface WhatIfAnalysisProps {
  baselineCost: number;
  scenarioCost: number;
  change?: number;
  changePercent?: number;
  riskChange: string;
  statusChange: string;
}

function safeNumber(
  value: number | undefined | null
): number {
  const numericValue = Number(value);

  return Number.isFinite(numericValue)
    ? numericValue
    : 0;
}

function formatINR(
  value: number | undefined | null
): string {
  const numericValue =
    safeNumber(value);

  return new Intl.NumberFormat(
    "en-IN",
    {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }
  ).format(numericValue);
}

function formatStatus(
  value: string | undefined | null
): string {
  return (value || "NO CHANGE")
    .replace(/_/g, " ")
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    );
}

function getRiskClass(
  value: string | undefined | null
): string {
  const risk =
    (value || "").toLowerCase();

  if (
    risk.includes("high") ||
    risk.includes("critical")
  ) {
    return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20";
  }

  if (
    risk.includes("medium")
  ) {
    return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20";
  }

  if (
    risk.includes("low")
  ) {
    return "bg-[#14B8A6]/10 text-[#14B8A6] border-[#14B8A6]/20";
  }

  return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/20";
}

function getStatusClass(
  value: string | undefined | null
): string {
  const status =
    (value || "").toLowerCase();

  if (
    status.includes("over_budget") ||
    status.includes("over budget")
  ) {
    return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20";
  }

  if (
    status.includes("at_risk") ||
    status.includes("at risk") ||
    status.includes("slightly")
  ) {
    return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20";
  }

  if (
    status.includes("within") ||
    status.includes("under")
  ) {
    return "bg-[#14B8A6]/10 text-[#14B8A6] border-[#14B8A6]/20";
  }

  return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/20";
}

export default function WhatIfAnalysis({
  baselineCost,
  scenarioCost,
  change,
  changePercent,
  riskChange,
  statusChange,
}: WhatIfAnalysisProps) {
  const safeBaselineCost =
    safeNumber(baselineCost);

  const safeScenarioCost =
    safeNumber(scenarioCost);

  /*
   * Calculate the change directly from
   * baseline and scenario whenever possible.
   *
   * This prevents the UI from displaying
   * ₹0 just because the comparison object
   * from the backend is missing a field.
   */
  const calculatedChange =
    safeScenarioCost -
    safeBaselineCost;

  const calculatedChangePercent =
    safeBaselineCost > 0
      ? (calculatedChange /
          safeBaselineCost) *
        100
      : 0;

  const safeChange =
    Number.isFinite(
      Number(change)
    )
      ? safeNumber(change)
      : calculatedChange;

  const safeChangePercent =
    Number.isFinite(
      Number(changePercent)
    )
      ? safeNumber(changePercent)
      : calculatedChangePercent;

  const costIncreased =
    safeChange > 0;

  const costDecreased =
    safeChange < 0;

  return (
    <div className="rounded-lg border border-[#253248] bg-[#0F1726] overflow-hidden">

      {/* HEADER */}
      <div className="px-4 py-3 border-b border-[#253248] flex items-center justify-between">

        <div className="flex items-center gap-2">

          <div className="w-7 h-7 rounded-md bg-[#8B5CF6]/10 flex items-center justify-center">

            <GitCompare
              size={14}
              className="text-[#8B5CF6]"
            />

          </div>

          <div>

            <h3 className="text-[12px] font-semibold text-[#F5F7FA]">
              What-If Cost Analysis
            </h3>

            <p className="text-[9px] text-[#667386] mt-0.5">
              Compare the baseline engineering plan with the proposed scenario
            </p>

          </div>

        </div>

        <span className="text-[9px] uppercase tracking-wide font-semibold text-[#8B5CF6]">
          Scenario Analysis
        </span>

      </div>

      {/* BASELINE → SCENARIO */}
      <div className="p-4">

        <div className="grid grid-cols-[1fr_auto_1fr] gap-4 items-stretch">

          {/* BASELINE */}
          <div className="rounded-lg border border-[#253248] bg-[#0A1220] p-4">

            <div className="flex items-center justify-between mb-3">

              <span className="text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Baseline
              </span>

              <span className="text-[8px] px-2 py-1 rounded bg-[#253248] text-[#9AA6B5]">
                CURRENT
              </span>

            </div>

            <p className="text-[9px] text-[#667386] mb-1">
              Current estimated cost
            </p>

            <p className="text-[22px] font-semibold font-mono text-[#F5F7FA]">
              {formatINR(
                safeBaselineCost
              )}
            </p>

          </div>

          {/* ARROW */}
          <div className="flex flex-col items-center justify-center px-1">

            <ArrowRight
              size={18}
              className="text-[#8B5CF6]"
            />

            <span className="text-[8px] text-[#667386] mt-1 whitespace-nowrap">
              WHAT-IF
            </span>

          </div>

          {/* SCENARIO */}
          <div
            className={`rounded-lg border p-4 ${
              costIncreased
                ? "border-[#EF4444]/30 bg-[#EF4444]/5"
                : costDecreased
                ? "border-[#14B8A6]/30 bg-[#14B8A6]/5"
                : "border-[#253248] bg-[#0A1220]"
            }`}
          >

            <div className="flex items-center justify-between mb-3">

              <span className="text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Scenario
              </span>

              <span
                className={`text-[8px] px-2 py-1 rounded ${
                  costIncreased
                    ? "bg-[#EF4444]/10 text-[#EF4444]"
                    : costDecreased
                    ? "bg-[#14B8A6]/10 text-[#14B8A6]"
                    : "bg-[#253248] text-[#9AA6B5]"
                }`}
              >
                PROPOSED
              </span>

            </div>

            <p className="text-[9px] text-[#667386] mb-1">
              Scenario estimated cost
            </p>

            <p
              className={`text-[22px] font-semibold font-mono ${
                costIncreased
                  ? "text-[#EF4444]"
                  : costDecreased
                  ? "text-[#14B8A6]"
                  : "text-[#F5F7FA]"
              }`}
            >
              {formatINR(
                safeScenarioCost
              )}
            </p>

          </div>

        </div>

        {/* COST IMPACT */}
        <div className="mt-4 rounded-lg border border-[#253248] bg-[#0A1220] p-4">

          <div className="flex items-center justify-between mb-3">

            <div>

              <p className="text-[11px] font-semibold text-[#F5F7FA]">
                Cost Impact
              </p>

              <p className="text-[9px] text-[#667386] mt-0.5">
                Difference between baseline and scenario
              </p>

            </div>

            <div
              className={`w-7 h-7 rounded-md flex items-center justify-center ${
                costIncreased
                  ? "bg-[#EF4444]/10"
                  : costDecreased
                  ? "bg-[#14B8A6]/10"
                  : "bg-[#253248]"
              }`}
            >

              {costIncreased ? (
                <TrendingUp
                  size={14}
                  className="text-[#EF4444]"
                />
              ) : costDecreased ? (
                <TrendingDown
                  size={14}
                  className="text-[#14B8A6]"
                />
              ) : (
                <CheckCircle2
                  size={14}
                  className="text-[#9AA6B5]"
                />
              )}

            </div>

          </div>

          <div className="flex items-end gap-3">

            <p
              className={`text-[20px] font-semibold font-mono ${
                costIncreased
                  ? "text-[#EF4444]"
                  : costDecreased
                  ? "text-[#14B8A6]"
                  : "text-[#F5F7FA]"
              }`}
            >
              {costIncreased
                ? "+"
                : ""}
              {formatINR(
                safeChange
              )}
            </p>

            <p
              className={`text-[11px] mb-1 ${
                costIncreased
                  ? "text-[#EF4444]"
                  : costDecreased
                  ? "text-[#14B8A6]"
                  : "text-[#9AA6B5]"
              }`}
            >
              {costIncreased
                ? "+"
                : ""}
              {safeChangePercent.toFixed(
                2
              )}
              %
            </p>

          </div>

        </div>

        {/* RISK + BUDGET STATUS */}
        <div className="grid grid-cols-2 gap-3 mt-3">

          {/* RISK */}
          <div className="rounded-lg border border-[#253248] bg-[#0A1220] p-3">

            <div className="flex items-center gap-2 mb-2">

              <AlertTriangle
                size={13}
                className="text-[#F59E0B]"
              />

              <span className="text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Risk Change
              </span>

            </div>

            <span
              className={`inline-flex rounded-md border px-2.5 py-1 text-[9px] font-semibold uppercase ${getRiskClass(
                riskChange
              )}`}
            >
              {formatStatus(
                riskChange
              )}
            </span>

          </div>

          {/* BUDGET STATUS */}
          <div className="rounded-lg border border-[#253248] bg-[#0A1220] p-3">

            <div className="flex items-center gap-2 mb-2">

              <CheckCircle2
                size={13}
                className="text-[#14B8A6]"
              />

              <span className="text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Budget Status
              </span>

            </div>

            <span
              className={`inline-flex rounded-md border px-2.5 py-1 text-[9px] font-semibold uppercase ${getStatusClass(
                statusChange
              )}`}
            >
              {formatStatus(
                statusChange
              )}
            </span>

          </div>

        </div>

        {/* EXPLANATION */}
        <div className="mt-3 px-3 py-2.5 rounded-md bg-[#141E2F] border border-[#253248]">

          <p className="text-[9px] text-[#9AA6B5] leading-relaxed">

            <span className="font-semibold text-[#F5F7FA]">
              Engineering decision support:
            </span>{" "}

            The scenario is recalculated using the same deterministic cost
            engine as the baseline. This makes the cost impact transparent
            before approving a design or quantity change.

          </p>

        </div>

      </div>

    </div>
  );
}