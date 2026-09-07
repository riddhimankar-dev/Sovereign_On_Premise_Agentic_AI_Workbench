import { BarChart3, CheckCircle2, Lightbulb, Table as TableIcon, TrendingUp } from "lucide-react";

interface MetricItem {
  name: string;
  value: string | number;
  unit?: string;
  status?: string;
}

interface FindingItem {
  title: string;
  detail?: string;
  confidence?: string;
}

interface ChartData {
  type?: string;
  title?: string;
  data?: Array<{ label?: string; value?: number }>;
}

interface TableData {
  title?: string;
  headers?: string[];
  rows?: Array<Array<string | number>>;
}

interface RecItem {
  priority?: string;
  action?: string;
  rationale?: string;
}

interface MultiParameterItem {
  parameter?: string;
  name?: string;
  actual?: number;
  limit?: number;
  deviation?: number;
  deviation_percent?: number;
  deviation_percentage?: number;
  unit?: string;
  status?: string;
  formula?: string;
  source?: string;
  source_ref?: string;
}

interface MultiParameterResult {
  parameter_count?: number;
  overall_status?: string;
  parameters?: MultiParameterItem[];
}

interface CalculationItem {
  calculation_id?: string;
  trace_id?: string;
  operation?: string;
  result?: unknown;
  unit?: string | null;
  formula?: string | null;
  verification_status?: string;
  status?: string;
}

export interface AnalysisEnvelope {
  summary?: string;
  findings?: FindingItem[];
  metrics?: MetricItem[];
  charts?: ChartData[];
  tables?: TableData[];
  recommendations?: RecItem[];
  calculations?: CalculationItem[];
}

function statusColor(status?: string) {
  switch ((status || "").toUpperCase()) {
    case "CRITICAL":
    case "IMMEDIATE_ESCALATION":
      return "bg-red-500/15 text-red-400 border-red-500/30";

    case "HIGH_CONCERN":
      return "bg-orange-500/15 text-orange-400 border-orange-500/30";

    case "WARNING":
    case "MONITORING":
    case "ENGINEERING_REVIEW":
      return "bg-amber-500/15 text-amber-400 border-amber-500/30";

    case "NORMAL":
      return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";

    default:
      return "bg-[#253248] text-[#9AA6B5] border-[#253248]";
  }
}

function BarChart({ chart }: { chart: ChartData }) {
  const data = (chart.data || []).filter((d) => typeof d.value === "number");
  const max = Math.max(...data.map((d) => d.value as number), 1);
  return (
    <div className="mt-3">
      <p className="text-[11px] text-[#667386] mb-2">{chart.title}</p>
      <div className="flex items-end gap-3 h-[90px] px-1">
        {data.map((d, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-1 min-w-0">
            <span className="text-[10px] font-semibold text-[#F5F7FA]">{d.value}</span>
            <div
              className="w-full rounded-[4px] bg-gradient-to-t from-[#8B5CF6] to-[#A78BFA] min-h-[4px]"
              style={{ height: `${Math.max(((d.value as number) / max) * 78, 4)}px` }}
            />
            <span className="text-[9px] text-[#667386] truncate w-full text-center">{d.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function LineChart({ chart }: { chart: ChartData }) {
  const data = (chart.data || []).filter((d) => typeof d.value === "number");
  if (data.length < 2) return <BarChart chart={chart} />;
  const w = 300;
  const h = 90;
  const max = Math.max(...data.map((d) => d.value as number), 1);
  const min = Math.min(...data.map((d) => d.value as number), 0);
  const range = max - min || 1;
  const step = data.length > 1 ? w / (data.length - 1) : w;
  const pts = data.map((d, i) => ({
    x: i * step,
    y: h - ((d.value as number) - min) / range * h,
    ...d,
  }));
  const path = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ");
  return (
    <div className="mt-3">
      <p className="text-[11px] text-[#667386] mb-2">{chart.title}</p>
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-[90px]">
        <polyline points={path} fill="none" stroke="#8B5CF6" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
        {pts.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="3" fill="#A78BFA" />
        ))}
      </svg>
      <div className="flex justify-between mt-1">
        {pts.map((p, i) => (
          <span key={i} className="text-[9px] text-[#667386] truncate max-w-[20%]">{p.label}</span>
        ))}
      </div>
    </div>
  );
}

function ChartCard({ chart }: { chart: ChartData }) {
  const type = (chart.type || "bar").toLowerCase();
  return (
    <div className="rounded-[10px] bg-[#141E2F] border border-[#253248] p-3.5">
      {type === "line" ? <LineChart chart={chart} /> : <BarChart chart={chart} />}
    </div>
  );
}

function isMultiParameterResult(
  result: unknown
): result is MultiParameterResult {
  if (!result || typeof result !== "object") return false;

  const value = result as MultiParameterResult;

  return Array.isArray(value.parameters);
}


function formatNumber(value: unknown, digits = 2): string {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "—";
  }

  return value.toFixed(digits);
}


function parameterStatusClass(status?: string): string {
  return statusColor(status);
}


function MultiParameterAnalysisCard({
  calculation,
}: {
  calculation: CalculationItem;
}) {
  if (!isMultiParameterResult(calculation.result)) {
    return null;
  }

  const result = calculation.result;
  const parameters = result.parameters || [];
  const overallStatus = result.overall_status || calculation.status || "NORMAL";

  return (
    <div className="rounded-[10px] bg-[#141E2F] border border-[#253248] overflow-hidden">
      
      {/* Header */}
      <div className="px-4 py-3 border-b border-[#253248] flex items-center gap-3">
        <div className="w-8 h-8 rounded-[7px] bg-[#8B5CF6]/12 flex items-center justify-center">
          <TableIcon size={14} className="text-[#8B5CF6]" />
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-[12.5px] font-semibold text-[#F5F7FA]">
            Multi-Parameter Engineering Analysis
          </p>

          <p className="text-[10px] text-[#667386] mt-0.5">
            {result.parameter_count ?? parameters.length} engineering parameter
            {(result.parameter_count ?? parameters.length) === 1 ? "" : "s"} analyzed
          </p>
        </div>

        <span
          className={`text-[9px] font-semibold px-2 py-1 rounded border ${statusColor(
            overallStatus
          )}`}
        >
          {overallStatus.replace(/_/g, " ")}
        </span>
      </div>

      {/* Parameter table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-[#253248] bg-[#0F1726]">
              <th className="px-3 py-2.5 text-[9px] font-semibold uppercase tracking-wide text-[#667386]">
                Parameter
              </th>

              <th className="px-3 py-2.5 text-[9px] font-semibold uppercase tracking-wide text-[#667386]">
                Actual
              </th>

              <th className="px-3 py-2.5 text-[9px] font-semibold uppercase tracking-wide text-[#667386]">
                Limit
              </th>

              <th className="px-3 py-2.5 text-[9px] font-semibold uppercase tracking-wide text-[#667386]">
                Deviation
              </th>

              <th className="px-3 py-2.5 text-[9px] font-semibold uppercase tracking-wide text-[#667386]">
                Dev. %
              </th>

              <th className="px-3 py-2.5 text-[9px] font-semibold uppercase tracking-wide text-[#667386]">
                Status
              </th>
            </tr>
          </thead>

          <tbody>
            {parameters.map((parameter, index) => {
              const parameterName =
                parameter.parameter ||
                parameter.name ||
                `Parameter ${index + 1}`;

              const deviationPercent =
                parameter.deviation_percent ??
                parameter.deviation_percentage;

              return (
                <tr
                  key={`${parameterName}-${index}`}
                  className="border-b border-[#253248]/70 last:border-b-0 hover:bg-[#182337] transition-colors"
                >
                  {/* Parameter */}
                  <td className="px-3 py-3">
                    <p className="text-[11.5px] font-medium text-[#F5F7FA]">
                      {parameterName}
                    </p>

                    {parameter.source && (
                      <p className="text-[9px] text-[#667386] mt-0.5 truncate max-w-[180px]">
                        {parameter.source}
                      </p>
                    )}
                  </td>

                  {/* Actual */}
                  <td className="px-3 py-3">
                    <span className="text-[11.5px] font-semibold text-[#F5F7FA]">
                      {formatNumber(parameter.actual)}
                    </span>

                    {parameter.unit && (
                      <span className="text-[9px] text-[#667386] ml-1">
                        {parameter.unit}
                      </span>
                    )}
                  </td>

                  {/* Limit */}
                  <td className="px-3 py-3">
                    <span className="text-[11.5px] text-[#9AA6B5]">
                      {formatNumber(parameter.limit)}
                    </span>

                    {parameter.unit && (
                      <span className="text-[9px] text-[#667386] ml-1">
                        {parameter.unit}
                      </span>
                    )}
                  </td>

                  {/* Deviation */}
                  <td className="px-3 py-3">
                    <span
                      className={`text-[11.5px] font-semibold ${
                        typeof parameter.deviation === "number" &&
                        parameter.deviation > 0
                          ? "text-[#F59E0B]"
                          : "text-[#9AA6B5]"
                      }`}
                    >
                      {typeof parameter.deviation === "number" &&
                      parameter.deviation > 0
                        ? "+"
                        : ""}
                      {formatNumber(parameter.deviation)}
                    </span>

                    {parameter.unit && (
                      <span className="text-[9px] text-[#667386] ml-1">
                        {parameter.unit}
                      </span>
                    )}
                  </td>

                  {/* Deviation percentage */}
                  <td className="px-3 py-3">
                    <span
                      className={`text-[11.5px] font-semibold ${
                        typeof deviationPercent === "number" &&
                        deviationPercent > 0
                          ? "text-[#F59E0B]"
                          : "text-[#9AA6B5]"
                      }`}
                    >
                      {typeof deviationPercent === "number" &&
                      deviationPercent > 0
                        ? "+"
                        : ""}
                      {formatNumber(deviationPercent)}%
                    </span>
                  </td>

                  {/* Status */}
                  <td className="px-3 py-3">
                    <span
                      className={`inline-flex whitespace-nowrap text-[9px] font-semibold px-1.5 py-1 rounded border ${parameterStatusClass(
                        parameter.status
                      )}`}
                    >
                      {(parameter.status || "NORMAL").replace(/_/g, " ")}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Formula + trace */}
      <div className="px-4 py-3 border-t border-[#253248] bg-[#0F1726] space-y-1.5">
        {calculation.formula && (
          <p className="text-[9.5px] text-[#9AA6B5] font-mono">
            Formula: {calculation.formula}
          </p>
        )}

        {calculation.calculation_id && (
          <p className="text-[9px] text-[#667386] font-mono">
            Calculation ID: {calculation.calculation_id}
          </p>
        )}

        {calculation.trace_id && (
          <p className="text-[9px] text-[#667386] font-mono">
            Trace ID: {calculation.trace_id}
          </p>
        )}

        <div className="flex items-center gap-1.5 pt-1">
          <CheckCircle2 size={11} className="text-[#22C55E]" />

          <span className="text-[9px] font-semibold text-[#22C55E]">
            {calculation.verification_status || "VERIFIED"}
          </span>

          <span className="text-[9px] text-[#667386]">
            · Deterministic Calculation Engine
          </span>
        </div>
      </div>
    </div>
  );
}

export default function AnalysisView({ analysis }: { analysis: AnalysisEnvelope }) {
  const findings = analysis.findings || [];
  const metrics = analysis.metrics || [];
  const charts = analysis.charts || [];
  const tables = analysis.tables || [];
  const recommendations = analysis.recommendations || [];
  const calculations = analysis.calculations || [];

  if (!analysis.summary && findings.length === 0 && metrics.length === 0 && calculations.length === 0) return null;

  return (
    <div className="mt-3 rounded-[10px] border border-[#253248] bg-[#0F1726] overflow-hidden animate-fade-up">
      <div className="px-4 py-2.5 border-b border-[#1a2740] flex items-center gap-2">
        <BarChart3 size={13} className="text-[#8B5CF6]" />
        <p className="text-[11px] font-semibold text-[#F5F7FA]">Structured Analysis</p>
      </div>
      <div className="p-4 space-y-4">
        {analysis.summary && (
          <p className="text-[12.5px] text-[#9AA6B5] leading-relaxed">{analysis.summary}</p>
        )}

        {metrics.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {metrics.map((m, i) => (
              <div key={i} className="rounded-[8px] bg-[#141E2F] border border-[#253248] px-3 py-2.5">
                <p className="text-[10px] text-[#667386]">{m.name}</p>
                <p className="text-[15px] font-semibold text-[#F5F7FA] mt-0.5">
                  {m.value}
                  {m.unit ? <span className="text-[10px] text-[#667386] ml-1">{m.unit}</span> : null}
                </p>
                <span className={`inline-block mt-1.5 text-[9px] font-semibold px-1.5 py-0.5 rounded border ${statusColor(m.status)}`}>
                  {m.status || "INFO"}
                </span>
              </div>
            ))}
          </div>
        )}

        {calculations.length > 0 && (
  <div>
    <p className="text-[10px] font-semibold uppercase tracking-wide text-[#667386] mb-2">
      Deterministic Calculations
    </p>

    <div className="space-y-3">
      {calculations.map((calculation, index) => {
        const isMultiParameter =
          calculation.operation === "multi_parameter_analysis" &&
          isMultiParameterResult(calculation.result);

        if (isMultiParameter) {
          return (
            <MultiParameterAnalysisCard
              key={calculation.calculation_id || index}
              calculation={calculation}
            />
          );
        }

        return (
          <div
            key={calculation.calculation_id || index}
            className="rounded-[8px] bg-[#141E2F] border border-[#253248] px-3 py-2.5"
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-[10px] text-[#667386] uppercase">
                {calculation.operation || "calculation"}
              </p>

              <span
                className={`text-[9px] font-semibold px-1.5 py-0.5 rounded border ${statusColor(
                  calculation.verification_status === "VERIFIED"
                    ? "NORMAL"
                    : "WARNING"
                )}`}
              >
                {calculation.verification_status || "PENDING"}
              </span>
            </div>

            <p className="text-[18px] font-semibold text-[#F5F7FA] mt-1">
              {typeof calculation.result === "object"
                ? JSON.stringify(calculation.result)
                : String(calculation.result ?? "-")}

              {calculation.unit ? (
                <span className="text-[10px] text-[#667386] ml-1">
                  {calculation.unit}
                </span>
              ) : null}
            </p>

            {calculation.formula && (
              <p className="text-[10px] text-[#9AA6B5] mt-1 font-mono">
                {calculation.formula}
              </p>
            )}

            {calculation.trace_id && (
              <p className="text-[9px] text-[#667386] mt-1 font-mono">
                Trace {calculation.trace_id}
              </p>
            )}
          </div>
        );
      })}
    </div>
  </div>
)}

        {charts.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {charts.map((c, i) => <ChartCard key={i} chart={c} />)}
          </div>
        )}

        {findings.length > 0 && (
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-wide text-[#667386] mb-2">Findings</p>
            <div className="space-y-2">
              {findings.map((f, i) => (
                <div key={i} className="rounded-[8px] bg-[#141E2F] border border-[#253248] px-3 py-2.5">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 size={12} className="text-[#8B5CF6] flex-none" />
                    <p className="text-[12px] font-medium text-[#F5F7FA] flex-1">{f.title}</p>
                    {f.confidence && (
                      <span className="text-[9px] font-semibold text-[#667386] uppercase">{f.confidence}</span>
                    )}
                  </div>
                  {f.detail && <p className="text-[11px] text-[#9AA6B5] mt-1 leading-relaxed">{f.detail}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {tables.length > 0 && (
          <div className="space-y-2">
            {tables.map((t, i) => (
              <div key={i} className="rounded-[8px] bg-[#141E2F] border border-[#253248] overflow-hidden">
                <div className="px-3 py-2 flex items-center gap-2 border-b border-[#1a2740]">
                  <TableIcon size={12} className="text-[#8B5CF6]" />
                  <p className="text-[11px] font-medium text-[#F5F7FA]">{t.title || "Data table"}</p>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr>
                        {(t.headers || []).map((h, j) => (
                          <th key={j} className="px-3 py-2 text-[10px] font-semibold text-[#667386]">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(t.rows || []).map((row, j) => (
                        <tr key={j}>
                          {row.map((cell, k) => (
                            <td key={k} className="px-3 py-1.5 text-[11px] text-[#9AA6B5]">{cell}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ))}
          </div>
        )}

        {recommendations.length > 0 && (
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-wide text-[#667386] mb-2">
              <span className="inline-flex items-center gap-1"><Lightbulb size={11} /> Recommendations</span>
            </p>
            <div className="space-y-2">
              {recommendations.map((r, i) => (
                <div key={i} className="rounded-[8px] bg-[#141E2F] border border-[#253248] px-3 py-2.5 flex items-start gap-2">
                  <TrendingUp size={12} className="text-[#8B5CF6] flex-none mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <p className="text-[12px] font-medium text-[#F5F7FA]">{r.action}</p>
                    {r.rationale && <p className="text-[11px] text-[#9AA6B5] mt-0.5">{r.rationale}</p>}
                  </div>
                  {r.priority && (
                    <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded border flex-none ${statusColor(r.priority)}`}>
                      {r.priority}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}