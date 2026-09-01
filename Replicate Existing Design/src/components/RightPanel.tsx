import { useState, useEffect } from "react";
import { X, ExternalLink } from "lucide-react";
import { api, ModelInfo, Artifact, SecurityStatusItem } from "../services/api";

interface RightPanelProps { onClose: () => void; }

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border-b border-[#1a2740] last:border-0 px-4 py-3.5">
      <p className="text-[9px] font-semibold tracking-[0.14em] text-[#3a4a60] uppercase mb-2.5">{title}</p>
      {children}
    </div>
  );
}

function readableName(modelId?: string): string {
  if (!modelId) return "Model";
  const parts = modelId.split(":");
  return parts[0] || modelId;
}

export default function RightPanel({ onClose }: RightPanelProps) {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [securityItems, setSecurityItems] = useState<SecurityStatusItem[]>([]);
  const [overall, setOverall] = useState<string>("secure");

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const data = await api.models.list();
        if (active) setModels(data.models || []);
      } catch { /* ignore */ }
      try {
        const art = await api.artifacts.list();
        if (active) setArtifacts(art.artifacts || []);
      } catch { /* ignore */ }
      try {
        const sec = await api.security.status();
        if (active) {
          setSecurityItems(sec.items || []);
          setOverall(sec.overall || "secure");
        }
      } catch { /* ignore */ }
    })();
    return () => { active = false; };
  }, []);

  const reasoning = models.find((m) => (m.role || "").toLowerCase().includes("reason")) || models[0];
  const ready = reasoning ? reasoning.status === "ready" || reasoning.status === "available" : false;

  const secureLabel = (label: string) => {
    const l = (label || "").toLowerCase();
    if (l.includes("internet")) return "Internet";
    if (l.includes("api")) return "External APIs";
    if (l.includes("cloud")) return "Cloud AI";
    if (l.includes("local model") || l.includes("inference")) return "Local inference";
    if (l.includes("storage")) return "Local storage";
    if (l.includes("audit")) return "Audit logging";
    return label;
  };

  return (
    <aside className="w-[260px] flex-none h-full flex flex-col bg-[#0F1726] border-l border-[#1a2740] overflow-y-auto animate-slide-right">
      <div className="h-12 flex items-center justify-between px-4 border-b border-[#1a2740] flex-none">
        <span className="text-[11px] font-semibold text-[#9AA6B5]">Context</span>
        <button onClick={onClose} className="w-6 h-6 rounded-[4px] flex items-center justify-center text-[#667386] hover:text-[#F5F7FA] hover:bg-[#141E2F] transition-all">
          <X size={12}/>
        </button>
      </div>

      <Section title="Active Model">
        {reasoning ? (
          <div className="rounded-[6px] bg-[#0A1220] border border-[#1a2740] px-3 py-2.5">
            <div className="flex items-start justify-between gap-2 mb-1">
              <p className="text-[11.5px] font-semibold text-[#F5F7FA] leading-snug">{readableName(reasoning.model_id)}</p>
              <div className="flex items-center gap-1 flex-none">
                <span className={`w-[5px] h-[5px] rounded-full ${ready ? "bg-[#22C55E]" : "bg-[#F59E0B]"}`}/>
                <span className={`text-[9px] font-medium ${ready ? "text-[#22C55E]" : "text-[#F59E0B]"}`}>{ready ? "Ready" : (reasoning.status || "Unknown")}</span>
              </div>
            </div>
            <p className="text-[10px] text-[#667386] capitalize">{reasoning.role || "Model"} · {reasoning.provider}</p>
            <div className="flex items-center gap-3 mt-1.5">
              <span className="text-[10px] text-[#9AA6B5] font-mono">{reasoning.context_length ? `${Math.round(reasoning.context_length / 1000)}K ctx` : "—"}</span>
              <span className="text-[10px] text-[#9AA6B5] font-mono">{reasoning.vram_usage_gb ? `${reasoning.vram_usage_gb} GB VRAM` : ""}</span>
            </div>
          </div>
        ) : (
          <p className="text-[11px] text-[#667386]">No models available.</p>
        )}
      </Section>

      <Section title="Context">
        <p className="text-[11px] text-[#667386] leading-relaxed">Session context is scoped to your current workspace and organization security policies.</p>
      </Section>

      <Section title="Sources">
        <p className="text-[11px] text-[#667386]">No sources yet.</p>
      </Section>

      <Section title="Artifacts">
        {artifacts.length === 0 ? (
          <p className="text-[11px] text-[#667386]">No artifacts yet.</p>
        ) : (
          <div className="space-y-1.5">
            {artifacts.slice(0, 4).map(a => (
              <div key={a.id} className="flex items-center gap-2 px-2.5 py-2 rounded-[6px] bg-[#0A1220] border border-[#1a2740] hover:border-[#253248] cursor-pointer group transition-all">
                <div className="w-5 h-5 rounded-[3px] bg-[#8B5CF6]/12 flex items-center justify-center flex-none">
                  <span className="text-[7px] font-bold text-[#8B5CF6]">ART</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[11px] font-medium text-[#F5F7FA] truncate">{a.name}</p>
                  <p className="text-[9.5px] text-[#9AA6B5] capitalize">{a.status}</p>
                </div>
                <ExternalLink size={10} className="text-[#3a4a60] opacity-0 group-hover:opacity-100 transition-opacity flex-none"/>
              </div>
            ))}
          </div>
        )}
      </Section>

      <Section title="Security">
        {securityItems.length > 0 ? (
          <div className="space-y-1.5">
            {securityItems.map((item) => (
              <div key={item.label} className="flex items-center justify-between">
                <p className="text-[10px] text-[#667386]">{secureLabel(item.label)}</p>
                <p className={`text-[9px] font-semibold tracking-wide ${item.status_color || "text-[#667386]"}`}>{item.status}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-[11px] text-[#667386]">{overall === "secure" ? "Environment secure." : `Overall: ${overall}`}</p>
        )}
        <div className="flex items-center gap-1.5 mt-2.5">
          <span className="w-[5px] h-[5px] rounded-full bg-[#14B8A6] animate-pulse-dot"/>
          <p className="text-[10px] text-[#14B8A6]">Your work stays within ApexPetro.</p>
        </div>
      </Section>
    </aside>
  );
}
