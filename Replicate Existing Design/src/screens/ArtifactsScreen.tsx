import { useState, useEffect } from "react";
import { FileText, FileSpreadsheet, Package, Eye, ExternalLink, Download, ChevronRight, AlertTriangle } from "lucide-react";
import { api, Artifact } from "../services/api";

const tabs = ["All", "Documents", "Spreadsheets", "Presentations", "Code", "Reports"];

function tabFor(type: string): string {
  const t = (type || "").toLowerCase();
  if (t.includes("sheet") || t.includes("xl")) return "Spreadsheets";
  if (t.includes("present") || t.includes("ppt")) return "Presentations";
  if (t.includes("report")) return "Reports";
  if (t.includes("code") || t.includes("py") || t.includes("script")) return "Code";
  return "Documents";
}

function iconFor(type: string) {
  const t = (type || "").toLowerCase();
  if (t.includes("sheet") || t.includes("xl")) return FileSpreadsheet;
  if (t.includes("code") || t.includes("py")) return Package;
  return FileText;
}

function extFor(name: string): string {
  const idx = name.lastIndexOf(".");
  return idx >= 0 ? name.slice(idx + 1).toUpperCase() : "DOC";
}

export default function ArtifactsScreen() {
  const [activeTab, setActiveTab] = useState("All");
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.artifacts.list();
        if (!active) return;
        setArtifacts(data.artifacts || []);
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "Failed to load artifacts");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  const statusText = (status: string) => (status || "Unknown").charAt(0).toUpperCase() + (status || "unknown").slice(1);
  const statusColor = (status: string) => {
    const s = (status || "").toLowerCase();
    if (s.includes("verified") || s.includes("approv") || s.includes("ready")) return "text-[#22C55E]";
    if (s.includes("pending") || s.includes("await")) return "text-[#F59E0B]";
    return "text-[#9AA6B5]";
  };

  const filtered = activeTab === "All" ? artifacts : artifacts.filter(a => tabFor(a.artifact_type) === activeTab);

  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      <div className="max-w-4xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h1 className="text-[22px] font-semibold text-[#F5F7FA]">Artifacts</h1>
            <p className="text-[12px] text-[#667386] mt-0.5">AI-generated deliverables · ApexPetro Energy Limited</p>
          </div>
        </div>

        <div className="flex items-center gap-1 mb-5 border-b border-[#253248] pb-0">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`h-9 px-3.5 text-[12px] font-medium border-b-2 transition-all -mb-px ${
                activeTab === tab
                  ? "text-[#8B5CF6] border-[#8B5CF6]"
                  : "text-[#667386] border-transparent hover:text-[#9AA6B5]"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {error && (
          <div className="rounded-xl bg-[#7F1D1D]/15 border border-[#7F1D1D]/40 px-4 py-3 flex items-start gap-2.5 mb-4">
            <AlertTriangle size={14} className="text-[#FCA5A5] flex-none mt-0.5" />
            <p className="text-[12.5px] text-[#FCA5A5]">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="space-y-2.5">
            {[0, 1, 2].map((i) => (
              <div key={i} className="rounded-xl bg-[#0F1726] border border-[#253248] p-5 animate-pulse">
                <div className="h-3 w-1/3 bg-[#253248] rounded mb-2" />
                <div className="h-2.5 w-2/3 bg-[#1a2740] rounded" />
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16">
            <Package size={32} className="text-[#253248] mx-auto mb-3" />
            <p className="text-[14px] text-[#667386]">No {activeTab.toLowerCase()} yet.</p>
            <p className="text-[12px] text-[#667386] mt-1">Generated deliverables will appear here.</p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {filtered.map((art) => {
              const Icon = iconFor(art.artifact_type);
              return (
                <div key={art.id} className="rounded-xl bg-[#0F1726] border border-[#253248] hover:border-[#2e3e57] transition-all group">
                  <div className="flex items-center gap-4 px-5 py-4">
                    <div className="w-10 h-10 rounded-xl bg-[#8B5CF6]/15 flex items-center justify-center flex-none">
                      <Icon size={18} className="text-[#8B5CF6]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-[13px] font-semibold text-[#F5F7FA]">{art.name}</p>
                        <span className="text-[9px] font-bold bg-[#253248] text-[#9AA6B5] px-1.5 py-0.5 rounded">{extFor(art.name)}</span>
                        <span className="text-[9px] font-semibold text-[#F59E0B] bg-[#F59E0B]/8 px-1.5 py-0.5 rounded">{art.classification}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <p className="text-[11px] text-[#667386]">{art.artifact_type}</p>
                        <span className="text-[#253248]">·</span>
                        <p className="text-[11px] text-[#667386]">{new Date(art.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-none">
                      <span className={`text-[11px] font-medium ${statusColor(art.status)}`}>{statusText(art.status)}</span>
                      <div className="flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button className="h-7 px-2.5 rounded-md text-[11px] text-[#9AA6B5] bg-[#141E2F] border border-[#253248] hover:text-[#F5F7FA] hover:border-[#2e3e57] transition-all flex items-center gap-1.5">
                          <Eye size={11} /> Preview
                        </button>
                        <button className="h-7 px-2.5 rounded-md text-[11px] text-[#9AA6B5] bg-[#141E2F] border border-[#253248] hover:text-[#F5F7FA] hover:border-[#2e3e57] transition-all flex items-center gap-1.5">
                          <ExternalLink size={11} /> Open
                        </button>
                        <a href={art.file_path || "#"} className="h-7 px-2.5 rounded-md text-[11px] text-[#8B5CF6] border border-[#8B5CF6]/25 hover:bg-[#8B5CF6]/10 transition-all flex items-center gap-1.5">
                          <Download size={11} />
                        </a>
                      </div>
                    </div>
                    <ChevronRight size={14} className="text-[#253248] group-hover:text-[#667386] transition-colors flex-none" />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
