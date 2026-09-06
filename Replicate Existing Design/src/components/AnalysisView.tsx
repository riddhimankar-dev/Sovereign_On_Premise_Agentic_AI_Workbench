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

export interface AnalysisEnvelope {
  summary?: string;
  findings?: FindingItem[];
  metrics?: MetricItem[];
  charts?: ChartData[];
  tables?: TableData[];
  recommendations?: RecItem[];
}

function statusColor(status?: string) {
  switch ((status || "").toUpperCase()) {
    case "CRITICAL":
      return "bg-red-500/15 text-red-400 border-red-500/30";
    case "WARNING":
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

export default function AnalysisView({ analysis }: { analysis: AnalysisEnvelope }) {
  const findings = analysis.findings || [];
  const metrics = analysis.metrics || [];
  const charts = analysis.charts || [];
  const tables = analysis.tables || [];
  const recommendations = analysis.recommendations || [];

  if (!analysis.summary && findings.length === 0 && metrics.length === 0) return null;

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