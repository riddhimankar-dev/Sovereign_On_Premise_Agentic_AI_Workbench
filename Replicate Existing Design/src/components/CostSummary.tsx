import {
  IndianRupee,
  TrendingUp,
  TrendingDown,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

interface CostSummaryProps {
  totalCost: number;
  budget: number;
  variance: number;
  variancePercent: number;
  riskLevel: string;
  budgetStatus: string;
}

function safeNumber(value: number | undefined | null): number {
  const numericValue = Number(value);

  return Number.isFinite(numericValue) ? numericValue : 0;
}

function formatINR(value: number | undefined | null): string {
  const numericValue = safeNumber(value);

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(numericValue);
}

function getRiskClasses(riskLevel: string | undefined): string {
  const risk = (riskLevel || "low").toLowerCase();

  if (risk === "low") {
    return "bg-[#14B8A6]/10 text-[#14B8A6] border-[#14B8A6]/20";
  }

  if (risk === "medium") {
    return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20";
  }

  return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20";
}

function getStatusClasses(status: string | undefined): string {
  const value = (status || "within_budget").toLowerCase();

  if (value === "within_budget") {
    return "bg-[#14B8A6]/10 text-[#14B8A6] border-[#14B8A6]/20";
  }

  if (
    value === "slightly_over_budget" ||
    value === "at_risk"
  ) {
    return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20";
  }

  return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20";
}

function formatLabel(value: string | undefined): string {
  return (value || "WITHIN_BUDGET")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default function CostSummary({
  totalCost,
  budget,
  variance,
  variancePercent,
  riskLevel,
  budgetStatus,
}: CostSummaryProps) {
  const safeTotalCost = safeNumber(totalCost);
  const safeBudget = safeNumber(budget);
  const safeVariance = safeNumber(variance);
  const safeVariancePercent = safeNumber(variancePercent);

  const isOverBudget = safeVariance > 0;

  const rawBudgetUsage =
    safeBudget > 0
      ? (safeTotalCost / safeBudget) * 100
      : 0;

  const budgetUsage = Math.min(
    Math.max(rawBudgetUsage, 0),
    100
  );

  return (
    <div className="space-y-3">

      {/* Main cost cards */}
      <div className="grid grid-cols-4 gap-3">

        {/* Total Cost */}
        <div className="rounded-lg border border-[#253248] bg-[#0F1726] p-4">

          <div className="flex items-center justify-between mb-3">

            <div className="flex items-center gap-2">

              <div className="w-7 h-7 rounded-md bg-[#8B5CF6]/10 flex items-center justify-center">

                <IndianRupee
                  size={14}
                  className="text-[#8B5CF6]"
                />

              </div>

              <span className="text-[10px] uppercase tracking-wide text-[#667386] font-semibold">
                Total Cost
              </span>

            </div>

          </div>

          <p className="text-[20px] font-semibold text-[#F5F7FA]">
            {formatINR(safeTotalCost)}
          </p>

          <p className="text-[10px] text-[#667386] mt-1">
            Estimated engineering cost
          </p>

        </div>

        {/* Budget */}
        <div className="rounded-lg border border-[#253248] bg-[#0F1726] p-4">

          <div className="flex items-center gap-2 mb-3">

            <div className="w-7 h-7 rounded-md bg-[#3B82F6]/10 flex items-center justify-center">

              <CheckCircle2
                size={14}
                className="text-[#3B82F6]"
              />

            </div>

            <span className="text-[10px] uppercase tracking-wide text-[#667386] font-semibold">
              Project Budget
            </span>

          </div>

          <p className="text-[20px] font-semibold text-[#F5F7FA]">
            {formatINR(safeBudget)}
          </p>

          <div className="mt-2">

            <div className="flex justify-between text-[9px] mb-1">

              <span className="text-[#667386]">
                Budget utilization
              </span>

              <span className="text-[#9AA6B5]">
                {rawBudgetUsage.toFixed(1)}%
              </span>

            </div>

            <div className="h-1.5 bg-[#253248] rounded-full overflow-hidden">

              <div
                className="h-full bg-[#8B5CF6] rounded-full transition-all"
                style={{
                  width: `${budgetUsage}%`,
                }}
              />

            </div>

          </div>

        </div>

        {/* Variance */}
        <div className="rounded-lg border border-[#253248] bg-[#0F1726] p-4">

          <div className="flex items-center gap-2 mb-3">

            <div
              className={`w-7 h-7 rounded-md flex items-center justify-center ${
                isOverBudget
                  ? "bg-[#EF4444]/10"
                  : "bg-[#14B8A6]/10"
              }`}
            >

              {isOverBudget ? (
                <TrendingUp
                  size={14}
                  className="text-[#EF4444]"
                />
              ) : (
                <TrendingDown
                  size={14}
                  className="text-[#14B8A6]"
                />
              )}

            </div>

            <span className="text-[10px] uppercase tracking-wide text-[#667386] font-semibold">
              Variance
            </span>

          </div>

          <p
            className={`text-[20px] font-semibold ${
              isOverBudget
                ? "text-[#EF4444]"
                : "text-[#14B8A6]"
            }`}
          >
            {isOverBudget ? "+" : ""}
            {formatINR(safeVariance)}
          </p>

          <p
            className={`text-[10px] mt-1 ${
              isOverBudget
                ? "text-[#EF4444]"
                : "text-[#14B8A6]"
            }`}
          >
            {isOverBudget ? "+" : ""}
            {safeVariancePercent.toFixed(2)}% from budget
          </p>

        </div>

        {/* Risk */}
        <div className="rounded-lg border border-[#253248] bg-[#0F1726] p-4">

          <div className="flex items-center gap-2 mb-3">

            <div className="w-7 h-7 rounded-md bg-[#F59E0B]/10 flex items-center justify-center">

              <ShieldAlert
                size={14}
                className="text-[#F59E0B]"
              />

            </div>

            <span className="text-[10px] uppercase tracking-wide text-[#667386] font-semibold">
              Risk Level
            </span>

          </div>

          <span
            className={`inline-flex items-center rounded-md border px-2.5 py-1 text-[11px] font-semibold uppercase ${getRiskClasses(
              riskLevel
            )}`}
          >
            {riskLevel || "LOW"}
          </span>

          <p className="text-[10px] text-[#667386] mt-2">
            Based on budget variance and project criticality
          </p>

        </div>

      </div>

      {/* Budget status bar */}
      <div className="rounded-lg border border-[#253248] bg-[#0F1726] px-4 py-3">

        <div className="flex items-center justify-between">

          <div className="flex items-center gap-2">

            {isOverBudget ? (
              <AlertTriangle
                size={15}
                className="text-[#F59E0B]"
              />
            ) : (
              <CheckCircle2
                size={15}
                className="text-[#14B8A6]"
              />
            )}

            <div>

              <p className="text-[11px] font-semibold text-[#F5F7FA]">
                Budget Status
              </p>

              <p className="text-[9px] text-[#667386] mt-0.5">
                Current estimate compared with approved project budget
              </p>

            </div>

          </div>

          <span
            className={`rounded-md border px-3 py-1.5 text-[10px] font-semibold uppercase ${getStatusClasses(
              budgetStatus
            )}`}
          >
            {formatLabel(budgetStatus)}
          </span>

        </div>

      </div>

    </div>
  );
}