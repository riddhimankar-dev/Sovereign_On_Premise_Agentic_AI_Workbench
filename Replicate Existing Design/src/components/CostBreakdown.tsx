import {
  Package,
  Wrench,
  Settings,
  ShieldAlert,
} from "lucide-react";

import type { CostItemResult } from "../services/api";

interface CostBreakdownProps {
  items: CostItemResult[];
}

function formatINR(value: number | undefined | null): string {
  const numericValue = Number(value);

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number.isFinite(numericValue) ? numericValue : 0);
}

function formatPercent(value: number | undefined | null): string {
  const numericValue = Number(value);

  return `${Number.isFinite(numericValue) ? numericValue.toFixed(1) : "0.0"}%`;
}

function getCriticalityClass(criticality: string | undefined): string {
  switch ((criticality || "low").toLowerCase()) {
    case "critical":
      return "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20";

    case "high":
      return "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20";

    case "medium":
      return "bg-[#3B82F6]/10 text-[#3B82F6] border-[#3B82F6]/20";

    default:
      return "bg-[#14B8A6]/10 text-[#14B8A6] border-[#14B8A6]/20";
  }
}

export default function CostBreakdown({
  items,
}: CostBreakdownProps) {
  if (!items || items.length === 0) {
    return (
      <div className="rounded-lg border border-[#253248] bg-[#0F1726] p-8 text-center">
        <Package
          size={24}
          className="mx-auto text-[#3a4a60] mb-2"
        />

        <p className="text-[12px] text-[#9AA6B5]">
          No engineering cost items available.
        </p>

        <p className="text-[10px] text-[#667386] mt-1">
          Add equipment or materials to generate a cost breakdown.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-[#253248] bg-[#0F1726] overflow-hidden">

      {/* Header */}
      <div className="px-4 py-3 border-b border-[#253248] flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Package
            size={15}
            className="text-[#8B5CF6]"
          />

          <div>
            <h3 className="text-[12px] font-semibold text-[#F5F7FA]">
              Engineering Cost Breakdown
            </h3>

            <p className="text-[9px] text-[#667386] mt-0.5">
              Deterministic equipment, installation, maintenance and contingency costs
            </p>
          </div>
        </div>

        <span className="text-[9px] font-mono text-[#667386]">
          {items.length} {items.length === 1 ? "ITEM" : "ITEMS"}
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] border-collapse">

          <thead>
            <tr className="border-b border-[#253248] bg-[#0A1220]">

              <th className="text-left px-4 py-3 text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Engineering Item
              </th>

              <th className="text-center px-3 py-3 text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Qty
              </th>

              <th className="text-right px-3 py-3 text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Equipment
              </th>

              <th className="text-right px-3 py-3 text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Installation
              </th>

              <th className="text-right px-3 py-3 text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Maintenance
              </th>

              <th className="text-right px-3 py-3 text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Contingency
              </th>

              <th className="text-right px-4 py-3 text-[9px] uppercase tracking-wide font-semibold text-[#667386]">
                Total
              </th>

            </tr>
          </thead>

          <tbody>
            {items.map((item, index) => (
              <tr
                key={`${item.name}-${index}`}
                className="border-b border-[#1a2740] last:border-b-0 hover:bg-[#141E2F]/60 transition-colors"
              >

                {/* Item */}
                <td className="px-4 py-3">
                  <div className="flex items-start gap-2.5">

                    <div className="w-7 h-7 rounded-md bg-[#8B5CF6]/10 flex items-center justify-center flex-none">

                      {item.category?.toLowerCase().includes("instrument") ? (
                        <Settings
                          size={13}
                          className="text-[#8B5CF6]"
                        />
                      ) : (
                        <Package
                          size={13}
                          className="text-[#8B5CF6]"
                        />
                      )}

                    </div>

                    <div className="min-w-0">

                      <p className="text-[11px] font-medium text-[#F5F7FA] truncate max-w-[190px]">
                        {item.name}
                      </p>

                      <div className="flex items-center gap-2 mt-1">

                        {item.category && (
                          <span className="text-[9px] text-[#667386]">
                            {item.category}
                          </span>
                        )}

                        {item.material && (
                          <>
                            <span className="text-[#3a4a60]">
                              •
                            </span>

                            <span className="text-[9px] text-[#667386] truncate max-w-[100px]">
                              {item.material}
                            </span>
                          </>
                        )}

                      </div>

                      <div className="flex items-center gap-1.5 mt-1.5">

                        {item.safety_critical && (
                          <span className="inline-flex items-center gap-1 text-[8px] font-semibold uppercase text-[#EF4444]">
                            <ShieldAlert size={9} />
                            Safety Critical
                          </span>
                        )}

                        <span
                          className={`inline-flex items-center rounded border px-1.5 py-0.5 text-[8px] font-semibold uppercase ${getCriticalityClass(
                            item.criticality
                          )}`}
                        >
                          {item.criticality || "low"}
                        </span>

                      </div>

                    </div>
                  </div>
                </td>

                {/* Quantity */}
                <td className="px-3 py-3 text-center">
                  <span className="inline-flex min-w-[30px] justify-center rounded bg-[#141E2F] border border-[#253248] px-2 py-1 text-[10px] font-mono text-[#F5F7FA]">
                    {item.quantity}
                  </span>
                </td>

                {/* Equipment */}
                <td className="px-3 py-3 text-right">

                  <p className="text-[10px] font-mono text-[#F5F7FA]">
                    {formatINR(item.equipment_cost)}
                  </p>

                  <p className="text-[8px] text-[#667386] mt-0.5">
                    Qty × unit cost
                  </p>

                </td>

                {/* Installation */}
                <td className="px-3 py-3 text-right">

                  <div className="flex items-center justify-end gap-1.5">

                    <Wrench
                      size={10}
                      className="text-[#667386]"
                    />

                    <span className="text-[10px] font-mono text-[#9AA6B5]">
                      {formatINR(item.installation_cost)}
                    </span>

                  </div>

                </td>

                {/* Maintenance */}
                <td className="px-3 py-3 text-right">

                  <div className="flex items-center justify-end gap-1.5">

                    <Settings
                      size={10}
                      className="text-[#667386]"
                    />

                    <span className="text-[10px] font-mono text-[#9AA6B5]">
                      {formatINR(item.maintenance_cost)}
                    </span>

                  </div>

                </td>

                {/* Contingency */}
                <td className="px-3 py-3 text-right">

                  <p className="text-[10px] font-mono text-[#F59E0B]">
                    {formatINR(item.contingency)}
                  </p>

                  <p className="text-[8px] text-[#667386] mt-0.5">
                    {formatPercent(item.contingency_rate)}
                  </p>

                </td>

                {/* Total */}
                <td className="px-4 py-3 text-right">

                  <p className="text-[11px] font-semibold font-mono text-[#F5F7FA]">
                    {formatINR(item.total_cost)}
                  </p>

                </td>

              </tr>
            ))}
          </tbody>

        </table>
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-[#0A1220] border-t border-[#253248] flex items-center justify-between">

        <div className="flex items-center gap-2">

          <div className="w-1.5 h-1.5 rounded-full bg-[#14B8A6]" />

          <span className="text-[9px] text-[#667386]">
            Calculated locally by Engineering Cost Engine
          </span>

        </div>

        <span className="text-[9px] font-mono text-[#667386]">
          DETERMINISTIC
        </span>

      </div>

    </div>
  );
}