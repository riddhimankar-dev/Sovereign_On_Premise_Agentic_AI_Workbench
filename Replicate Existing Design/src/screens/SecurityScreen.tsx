import { useState, useEffect } from "react";
import { Shield, Wifi, Server, Cloud, Cpu, HardDrive, Terminal, FileSearch, Check, X, AlertTriangle } from "lucide-react";
import { api, SecurityStatusItem } from "../services/api";

function iconForLabel(label: string) {
  const l = (label || "").toLowerCase();
  if (l.includes("internet")) return Wifi;
  if (l.includes("api") || l.includes("external")) return Cloud;
  if (l.includes("cloud")) return Server;
  if (l.includes("local model") || l.includes("inference")) return Cpu;
  if (l.includes("storage")) return HardDrive;
  if (l.includes("sandbox") || l.includes("network") || l.includes("code")) return Terminal;
  if (l.includes("audit") || l.includes("log")) return FileSearch;
  return Shield;
}

function StatusIcon({ indicator }: { indicator: "active" | "blocked" | "disabled" }) {
  if (indicator === "active") return <Check size={14} className="text-[#14B8A6]" />;
  if (indicator === "blocked") return <X size={14} className="text-[#EF4444]" />;
  return <AlertTriangle size={14} className="text-[#667386]" />;
}

export default function SecurityScreen() {
  const [items, setItems] = useState<SecurityStatusItem[]>([]);
  const [overall, setOverall] = useState<"secure" | "degraded" | "warning">("secure");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.security.status();
        if (!active) return;
        setItems(data.items || []);
        setOverall(data.overall || "secure");
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "Failed to load security status");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  const overallColor = overall === "secure" ? "text-[#14B8A6] bg-[#14B8A6]/10 border-[#14B8A6]/25" : overall === "warning" ? "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/25" : "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/25";

  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      <div className="max-w-3xl mx-auto px-6 py-6">
        <div className="text-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-[#14B8A6]/12 border border-[#14B8A6]/20 flex items-center justify-center mx-auto mb-4">
            <Shield size={26} className="text-[#14B8A6]" />
          </div>
          <h1 className="text-[24px] font-semibold text-[#F5F7FA] mb-2">Your Secure Environment</h1>
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border mb-3 ${overallColor}`}>
            <span className="w-2 h-2 rounded-full bg-[#14B8A6] animate-pulse-dot" />
            <span className="text-[13px] font-semibold tracking-wide uppercase">{overall === "secure" ? "LOCAL ONLY" : overall}</span>
          </div>
          <p className="text-[13px] text-[#9AA6B5] max-w-xl mx-auto leading-relaxed">
            Your organization's AI environment operates entirely within its controlled infrastructure.
            Your work stays inside ApexPetro's environment.
          </p>
        </div>

        {error && (
          <div className="rounded-xl bg-[#7F1D1D]/15 border border-[#7F1D1D]/40 px-4 py-3 flex items-start gap-2.5 mb-4">
            <AlertTriangle size={14} className="text-[#FCA5A5] flex-none mt-0.5" />
            <p className="text-[12.5px] text-[#FCA5A5]">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="space-y-2.5">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="rounded-xl bg-[#0F1726] border border-[#253248] p-5 animate-pulse">
                <div className="h-3 w-1/3 bg-[#253248] rounded mb-2" />
                <div className="h-2.5 w-2/3 bg-[#1a2740] rounded" />
              </div>
            ))}
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-16">
            <Shield size={32} className="text-[#253248] mx-auto mb-3" />
            <p className="text-[14px] text-[#667386]">No security status available.</p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {items.map((item) => {
              const Icon = iconForLabel(item.label);
              return (
                <div key={item.label} className="rounded-xl bg-[#0F1726] border border-[#253248] px-5 py-4 flex items-start gap-4">
                  <div className="w-9 h-9 rounded-lg bg-[#141E2F] border border-[#253248] flex items-center justify-center flex-none">
                    <Icon size={16} className="text-[#9AA6B5]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-3 mb-1">
                      <p className="text-[13px] font-semibold text-[#F5F7FA]">{item.label}</p>
                      <span className={`flex items-center gap-1.5 text-[10px] font-semibold px-2 py-1 rounded-md border ${item.status_bg} ${item.status_color}`}>
                        <StatusIcon indicator={item.indicator} />
                        {item.status}
                      </span>
                    </div>
                    <p className="text-[12px] text-[#9AA6B5] leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="mt-6 rounded-xl bg-[#141E2F] border border-[#253248] px-5 py-4">
          <p className="text-[11px] text-[#667386] leading-relaxed">
            Security status reflects the architecture of your AI environment. For a full audit log or compliance report,
            contact your organization's IT security team. This interface communicates system configuration, not runtime verification.
          </p>
        </div>
      </div>
    </div>
  );
}
