import { useState, useEffect } from "react";
import { Check, Cpu, Zap, Code, Loader2, AlertTriangle } from "lucide-react";
import { api, ModelInfo } from "../services/api";

function tagFor(role: string): { tag: string; tagColor: string } {
  const r = (role || "general").toLowerCase();
  if (r.includes("reason")) return { tag: "LOCAL REASONING", tagColor: "bg-[#14B8A6]/12 text-[#14B8A6]" };
  if (r.includes("cod")) return { tag: "LOCAL CODING", tagColor: "bg-[#F59E0B]/12 text-[#F59E0B]" };
  if (r.includes("embed")) return { tag: "LOCAL EMBEDDING", tagColor: "bg-[#3B82F6]/12 text-[#3B82F6]" };
  if (r.includes("router")) return { tag: "ROUTER", tagColor: "bg-[#A78BFA]/12 text-[#A78BFA]" };
  return { tag: "LOCAL MODEL", tagColor: "bg-[#8B5CF6]/12 text-[#8B5CF6]" };
}

function iconFor(role: string) {
  const r = (role || "").toLowerCase();
  if (r.includes("cod")) return Code;
  if (r.includes("embed") || r.includes("router")) return Zap;
  return Cpu;
}

function readableName(modelId?: string): string {
  if (!modelId) return "Model";
  const parts = modelId.split(":");
  return parts[0] || modelId;
}

export default function ModelsScreen() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const data = await api.models.list();
        if (!active) return;
        setModels(data.models || []);
        const reasoning = data.models?.find((m) => (m.role || "").toLowerCase().includes("reason"));
        if (reasoning) setSelected(reasoning.model_id);
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "Failed to load models");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      <div className="max-w-3xl mx-auto px-6 py-6">
        <div className="mb-6">
          <h1 className="text-[22px] font-semibold text-[#F5F7FA] mb-1">AI Models</h1>
          <p className="text-[12px] text-[#667386]">Local models available in your environment. Select the model for your next conversation.</p>
          <div className="flex items-center gap-4 mt-3">
            {[
              { label: "Local inference", color: "text-[#14B8A6]" },
              { label: "No external API", color: "text-[#14B8A6]" },
              { label: "Workspace-approved", color: "text-[#14B8A6]" },
            ].map(({ label, color }) => (
              <div key={label} className="flex items-center gap-1.5">
                <Check size={11} className={color} />
                <span className="text-[11px] text-[#9AA6B5]">{label}</span>
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="rounded-xl bg-[#7F1D1D]/15 border border-[#7F1D1D]/40 px-4 py-3 flex items-start gap-2.5 mb-4">
            <AlertTriangle size={14} className="text-[#FCA5A5] flex-none mt-0.5" />
            <p className="text-[12.5px] text-[#FCA5A5]">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="space-y-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="rounded-xl bg-[#0F1726] border border-[#253248] p-5 animate-pulse">
                <div className="h-3 w-1/3 bg-[#253248] rounded mb-2" />
                <div className="h-2.5 w-2/3 bg-[#1a2740] rounded" />
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {models.map((model) => {
              const isSelected = selected === model.model_id;
              const Icon = iconFor(model.role);
              const { tag, tagColor } = tagFor(model.role);
              const ready = model.status === "ready" || model.status === "available";
              return (
                <div
                  key={model.model_id}
                  onClick={() => setSelected(model.model_id)}
                  className={`rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? "bg-[#141E2F] border-[#8B5CF6]/40"
                      : "bg-[#0F1726] border-[#253248] hover:border-[#2e3e57]"
                  }`}
                >
                  <div className="px-5 py-4">
                    <div className="flex items-start gap-4">
                      <div className={`w-10 h-10 rounded-xl ${isSelected ? "bg-[#8B5CF6]/12" : "bg-[#141E2F]"} flex items-center justify-center flex-none`}>
                        <Icon size={18} className="text-[#8B5CF6]" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <span className={`text-[9px] font-semibold tracking-wide px-1.5 py-0.5 rounded ${tagColor}`}>{tag}</span>
                          <span className={`ml-auto text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                            ready ? "text-[#22C55E] bg-[#22C55E]/10" : "text-[#F59E0B] bg-[#F59E0B]/10"
                          }`}>
                            {ready ? "Ready" : model.status || "Unknown"}
                          </span>
                        </div>
                        <h3 className="text-[14px] font-semibold text-[#F5F7FA] break-all">{readableName(model.model_id)}</h3>
                        <p className="text-[10px] text-[#667386] font-mono mt-0.5">{model.model_id}</p>
                        <p className="text-[11px] text-[#9AA6B5] mt-1.5 leading-relaxed capitalize">{model.role} · {model.provider}</p>

                        {model.capabilities && model.capabilities.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mt-2.5 mb-3">
                            {model.capabilities.map((p) => (
                              <span key={p} className="text-[10px] bg-[#253248] text-[#9AA6B5] rounded-md px-2 py-0.5 capitalize">{p}</span>
                            ))}
                          </div>
                        )}

                        <div className="flex items-center gap-4 pt-2.5 border-t border-[#253248]">
                          <div>
                            <p className="text-[9px] text-[#667386]">Context window</p>
                            <p className="text-[12px] font-mono font-semibold text-[#9AA6B5]">{model.context_length ? `${model.context_length.toLocaleString()}` : "—"}</p>
                          </div>
                          <div>
                            <p className="text-[9px] text-[#667386]">VRAM usage</p>
                            <p className="text-[12px] font-mono font-semibold text-[#9AA6B5]">{model.vram_usage_gb ? `${model.vram_usage_gb} GB` : "—"}</p>
                          </div>
                        </div>
                      </div>
                      <div className={`w-5 h-5 rounded-full border-2 flex-none mt-1 flex items-center justify-center transition-all ${
                        isSelected ? "border-[#8B5CF6] bg-[#8B5CF6]" : "border-[#253248]"
                      }`}>
                        {isSelected && <Check size={11} className="text-white" />}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}

            {models.length === 0 && (
              <div className="rounded-xl bg-[#0F1726] border border-[#253248] px-5 py-10 text-center">
                <p className="text-[13px] text-[#9AA6B5]">No models available.</p>
              </div>
            )}
          </div>
        )}

        <div className="mt-5">
          <button
            onClick={() => { if (selected) localStorage.setItem("sovereign_model", selected); }}
            disabled={!selected}
            className="w-full h-10 rounded-xl bg-[#8B5CF6] hover:bg-[#7C3AED] disabled:opacity-50 text-white text-[13px] font-semibold transition-colors flex items-center justify-center gap-2"
          >
            <Zap size={14} />
            Apply to Next Conversation
          </button>
          <p className="text-center text-[11px] text-[#667386] mt-2">{loading ? "Loading models…" : "Model selection applies to your next chat session."}</p>
        </div>
      </div>
    </div>
  );
}
