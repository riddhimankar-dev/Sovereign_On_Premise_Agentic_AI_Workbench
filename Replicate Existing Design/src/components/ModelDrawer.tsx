import { useState, useEffect } from "react";
import { X, Check, Zap, Loader2 } from "lucide-react";
import { api, ModelInfo } from "../services/api";

interface ModelDrawerProps {
  onClose: () => void;
}

function tagFor(role: string): string {
  const r = (role || "general").toLowerCase();
  if (r.includes("reason")) return "LOCAL REASONING";
  if (r.includes("cod")) return "LOCAL CODING";
  if (r.includes("embed")) return "LOCAL EMBEDDING";
  if (r.includes("router")) return "ROUTER";
  return "LOCAL MODEL";
}

function readableName(modelId?: string): string {
  if (!modelId) return "Model";
  const parts = modelId.split(":");
  return parts[0] || modelId;
}

export default function ModelDrawer({ onClose }: ModelDrawerProps) {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
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
      } catch {
        /* ignore */
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  function apply() {
    if (selected) localStorage.setItem("sovereign_model", selected);
    onClose();
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-end" onClick={onClose}>
      <div
        className="w-[480px] h-full bg-[#0F1726] border-l border-[#253248] flex flex-col animate-slide-right shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-5 border-b border-[#253248]">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-[16px] font-semibold text-[#F5F7FA]">Choose AI Model</h2>
              <p className="text-[12px] text-[#667386] mt-0.5">Available models are approved for your workspace.</p>
            </div>
            <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center text-[#667386] hover:text-[#F5F7FA] hover:bg-[#141E2F] transition-all">
              <X size={16} />
            </button>
          </div>

          <div className="flex items-center gap-4 mt-4">
            {["Local inference", "No external API", "Workspace-approved"].map((badge) => (
              <div key={badge} className="flex items-center gap-1.5">
                <Check size={11} className="text-[#14B8A6]" />
                <span className="text-[11px] text-[#9AA6B5]">{badge}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
          {loading ? (
            <div className="flex items-center justify-center gap-2 text-[12px] text-[#667386] py-10">
              <Loader2 size={14} className="animate-spin" /> Loading models…
            </div>
          ) : (
            models.map((model) => {
              const isSelected = selected === model.model_id;
              const ready = model.status === "ready" || model.status === "available";
              const isEmbedding = (model.role || "").toLowerCase().includes("embed");
              return (
                <div
                  key={model.model_id}
                  onClick={() => setSelected(model.model_id)}
                  className={`rounded-lg border p-4 cursor-pointer transition-all ${
                    isSelected
                      ? "bg-[#8B5CF6]/10 border-[#8B5CF6]/40"
                      : "bg-[#141E2F] border-[#253248] hover:border-[#2e3e57]"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-[9px] font-semibold tracking-wider px-1.5 py-0.5 rounded ${
                          isSelected ? "bg-[#8B5CF6]/20 text-[#8B5CF6]" : "bg-[#14B8A6]/12 text-[#14B8A6]"
                        }`}>
                          {tagFor(model.role)}
                        </span>
                      </div>
                      <p className="text-[13px] font-semibold text-[#F5F7FA] break-all">{readableName(model.model_id)}</p>
                      <p className="text-[10px] text-[#667386] font-mono mt-0.5">{model.model_id}</p>
                      <p className="text-[11px] text-[#9AA6B5] mt-1 leading-relaxed capitalize">{model.role}</p>
                    </div>
                    <div className={`w-5 h-5 rounded-full border-2 flex-none mt-0.5 flex items-center justify-center transition-all ${
                      isSelected ? "border-[#8B5CF6] bg-[#8B5CF6]" : "border-[#253248]"
                    }`}>
                      {isSelected && <Check size={11} className="text-white" />}
                    </div>
                  </div>

                  {model.capabilities && model.capabilities.length > 0 && !isEmbedding && (
                    <div className="mt-3">
                      <div className="flex flex-wrap gap-1">
                        {model.capabilities.map((cap) => (
                          <span key={cap} className="text-[10px] bg-[#253248] text-[#9AA6B5] rounded-md px-2 py-0.5 capitalize">{cap}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {!isEmbedding && (
                    <div className="flex items-center gap-4 mt-3 pt-3 border-t border-[#253248]">
                      <div>
                        <p className="text-[9px] text-[#667386]">Context</p>
                        <p className="text-[11px] font-mono font-medium text-[#9AA6B5]">{model.context_length ? model.context_length.toLocaleString() : "—"}</p>
                      </div>
                      <div>
                        <p className="text-[9px] text-[#667386]">VRAM</p>
                        <p className="text-[11px] font-mono font-medium text-[#9AA6B5]">{model.vram_usage_gb ? `${model.vram_usage_gb} GB` : "—"}</p>
                      </div>
                      <div className="ml-auto">
                        <div className="flex items-center gap-1">
                          <span className={`w-1.5 h-1.5 rounded-full ${ready ? "bg-[#22C55E]" : "bg-[#F59E0B]"}`} />
                          <span className={`text-[10px] font-medium ${ready ? "text-[#22C55E]" : "text-[#F59E0B]"}`}>
                            {ready ? "Ready" : model.status || "Unknown"}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        <div className="px-6 py-4 border-t border-[#253248]">
          <button
            onClick={apply}
            disabled={!selected}
            className="w-full h-10 bg-[#8B5CF6] hover:bg-[#7C3AED] disabled:opacity-50 text-white text-[13px] font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <Zap size={14} />
            Apply Model Selection
          </button>
        </div>
      </div>
    </div>
  );
}
