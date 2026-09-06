import { useState, useEffect } from "react";
import type { ReactNode } from "react";
import {
  ArrowLeft, AlertTriangle, Clock, FileText, Package, ClipboardCheck,
  CheckSquare, Zap, ExternalLink, Eye, Download, Check, ChevronRight,
  FileSpreadsheet, Loader,
} from "lucide-react";
import { api, Project, Document, Task, Artifact, Approval } from "../services/api";

interface ProjectDetailScreenProps {
  project: Project | null;
  onBack: () => void;
}

const tabs = ["Overview", "Files", "AI Tasks", "Artifacts", "Approvals"];

function StatBadge({ children, tone }: { children: ReactNode; tone: "green" | "amber" | "red" | "neutral" }) {
  const cls = {
    green: "text-[#22C55E] bg-[#22C55E]/10 border-[#22C55E]/20",
    amber: "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20",
    red: "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20",
    neutral: "text-[#9AA6B5] bg-[#253248] border-[#253248]",
  }[tone];
  return <span className={`flex items-center gap-1.5 text-[11px] font-bold px-2.5 py-1 rounded-lg border ${cls}`}>{children}</span>;
}

function riskTone(risk: string) {
  if ((risk || "").toUpperCase() === "HIGH") return "red" as const;
  if ((risk || "").toUpperCase() === "MEDIUM") return "amber" as const;
  return "green" as const;
}

export default function ProjectDetailScreen({ project, onBack }: ProjectDetailScreenProps) {
  const [activeTab, setActiveTab] = useState("Overview");
  const [docs, setDocs] = useState<Document[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!project) return;
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const [docsRes, tasksRes, artsRes, apprRes] = await Promise.all([
          api.documents.list(),
          api.tasks.list({ project_id: project.id }),
          api.artifacts.list({ project_id: project.id }),
          api.approvals.list(),
        ]);
        if (!active) return;
        const assetMatch = (doc: Document) =>
          !project.asset || project.asset === "—" || doc.file_name.toUpperCase().includes(project.asset.toUpperCase());
        setDocs(docsRes.documents.filter(assetMatch));
        setTasks(tasksRes.tasks || []);
        setArtifacts(artsRes.artifacts.filter((a) => a.project_id === project.id));
        setApprovals(apprRes.approvals || []);
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "Failed to load project details");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [project]);

  if (!project) {
    return (
      <div className="h-full flex flex-col bg-[#080D18] items-center justify-center">
        <p className="text-[12px] text-[#667386]">No project selected.</p>
        <button onClick={onBack} className="mt-4 text-[11px] text-[#8B5CF6] hover:underline">Back to Projects</button>
      </div>
    );
  }

  const p = project;
  const createdAt = p.created_at ? new Date(p.created_at).toLocaleString() : "—";
  const updatedAt = p.updated_at ? new Date(p.updated_at).toLocaleString() : "—";

  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-[#080D18] border-b border-[#253248]">
        <div className="max-w-5xl mx-auto px-6 py-4">
          <button
            onClick={onBack}
            className="flex items-center gap-1.5 text-[11px] text-[#667386] hover:text-[#9AA6B5] transition-colors mb-4"
          >
            <ArrowLeft size={13} /> Back to Projects
          </button>

          <div className="flex items-start justify-between gap-6">
            <div>
              <div className="flex items-center gap-1.5 text-[10px] text-[#667386] mb-2 flex-wrap">
                <span>ApexPetro Energy Limited</span>
                <ChevronRight size={10} />
                <span>{p.unit || "—"}</span>
                {p.asset && p.asset !== "—" && (
                  <>
                    <ChevronRight size={10} />
                    <span className="text-[#9AA6B5] font-medium">{p.asset}</span>
                  </>
                )}
              </div>

              <h1 className="text-[22px] font-semibold text-[#F5F7FA]">{p.name}</h1>
              <p className="text-[12px] text-[#667386] mt-0.5">{p.description || `${p.unit || "Unit"} · ${p.asset || "Asset not specified"}`}</p>
            </div>

            <div className="flex items-center gap-2 flex-none">
              {p.risk && p.risk !== "—" && (
                <StatBadge tone={riskTone(p.risk)}>
                  <AlertTriangle size={12} />
                  {p.risk} RISK
                </StatBadge>
              )}
              <StatBadge tone={p.status === "Completed" ? "green" : "amber"}>
                {p.status}
              </StatBadge>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-0 mt-5 border-b border-[#253248] -mb-px">
            {tabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`h-9 px-4 text-[12px] font-medium border-b-2 transition-all ${
                  activeTab === tab
                    ? "text-[#8B5CF6] border-[#8B5CF6]"
                    : "text-[#667386] border-transparent hover:text-[#9AA6B5]"
                }`}
              >
                {tab}
                {tab === "Approvals" && approvals.length > 0 && (
                  <span className="ml-1.5 text-[9px] bg-[#F59E0B]/20 text-[#F59E0B] px-1 py-0.5 rounded-full">
                    {approvals.filter((a) => a.status.toUpperCase() === "PENDING").length}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader size={24} className="text-[#8B5CF6] animate-spin" />
          </div>
        ) : error ? (
          <div className="rounded-xl bg-[#7F1D1D]/15 border border-[#7F1D1D]/40 px-4 py-3 text-[12px] text-[#FCA5A5]">
            {error}
          </div>
        ) : (
          <>
          {activeTab === "Overview" && (
            <div className="space-y-5">
              {p.description && (
                <div className="rounded-xl bg-[#0F1726] border border-[#253248] p-5">
                  <p className="text-[11px] font-semibold text-[#667386] uppercase tracking-widest mb-2">Description</p>
                  <p className="text-[13px] text-[#F5F7FA] leading-relaxed">{p.description}</p>
                </div>
              )}

              <div className="rounded-xl bg-[#0F1726] border border-[#253248] p-5">
                <p className="text-[11px] font-semibold text-[#667386] uppercase tracking-widest mb-3">Project Information</p>
                <div className="grid grid-cols-2 gap-y-3 gap-x-8">
                  {[
                    { label: "Company", value: "ApexPetro Energy Limited" },
                    { label: "Unit", value: p.unit || "—" },
                    { label: "Asset", value: p.asset || "—" },
                    { label: "Status", value: p.status },
                    { label: "Risk", value: p.risk || "—", color: riskTone(p.risk) === "red" ? "text-[#EF4444]" : "text-[#9AA6B5]" },
                    { label: "Progress", value: `${p.progress}%` },
                    { label: "Classification", value: p.classification, color: "text-[#F59E0B]" },
                    { label: "Created", value: createdAt },
                    { label: "Last Activity", value: updatedAt },
                    { label: "Code", value: p.project_id },
                  ].map(({ label, value, color }) => (
                    <div key={label} className="flex items-start justify-between gap-2">
                      <p className="text-[11px] text-[#667386] flex-none">{label}</p>
                      <p className={`text-[11px] text-right leading-snug ${color || "text-[#9AA6B5]"}`}>{value}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl bg-[#0F1726] border border-[#253248] p-5">
                <p className="text-[11px] font-semibold text-[#667386] uppercase tracking-widest mb-3">Linked Data</p>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { label: "Files", value: docs.length, icon: FileText, color: "text-[#8B5CF6]" },
                    { label: "Tasks", value: tasks.length, icon: ClipboardCheck, color: "text-[#14B8A6]" },
                    { label: "Artifacts", value: artifacts.length, icon: Package, color: "text-[#22C55E]" },
                  ].map(({ label, value, icon: Icon, color }) => (
                    <div key={label} className="rounded-lg bg-[#141E2F] border border-[#253248] p-3 flex items-center gap-3">
                      <Icon size={16} className={color} />
                      <div>
                        <p className="text-[18px] font-semibold text-[#F5F7FA] leading-none">{value}</p>
                        <p className="text-[10px] text-[#667386] mt-1">{label}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === "Files" && (
            docs.length === 0 ? (
              <div className="text-center py-16">
                <FileText size={28} className="text-[#253248] mx-auto mb-3" />
                <p className="text-[13px] text-[#667386]">No documents linked to this project yet</p>
              </div>
            ) : (
              <div className="space-y-2">
                {docs.map((doc) => {
                  const isPdf = (doc.file_type || "").toLowerCase() === "pdf";
                  const isXlsx = (doc.file_type || "").toLowerCase() === "xlsx";
                  const Icon = isXlsx ? FileSpreadsheet : FileText;
                  const iconColor = isXlsx ? "text-[#22C55E]" : "text-[#8B5CF6]";
                  return (
                    <div key={doc.document_id} className="flex items-center gap-4 px-5 py-3.5 rounded-xl bg-[#0F1726] border border-[#253248] hover:border-[#2e3e57] transition-all group">
                      <div className="w-9 h-9 rounded-lg bg-[#141E2F] flex items-center justify-center flex-none">
                        <Icon size={16} className={iconColor} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-[13px] font-medium text-[#F5F7FA] truncate">{doc.file_name}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-[9px] bg-[#253248] text-[#9AA6B5] px-1.5 py-0.5 rounded font-bold">{doc.file_type.toUpperCase()}</span>
                          <span className="text-[10px] text-[#667386]">{(doc.file_size / 1024 / 1024).toFixed(1)} MB</span>
                          <span className="text-[9px] text-[#F59E0B] font-semibold">{doc.classification}</span>
                        </div>
                      </div>
                      <span className="flex items-center gap-1 text-[10px] text-[#22C55E]">
                        <Check size={10} /> {doc.status}
                      </span>
                    </div>
                  );
                })}
              </div>
            )
          )}

          {activeTab === "AI Tasks" && (
            tasks.length === 0 ? (
              <div className="text-center py-16">
                <ClipboardCheck size={28} className="text-[#253248] mx-auto mb-3" />
                <p className="text-[13px] text-[#667386]">No tasks created for this project yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {tasks.map((task) => (
                  <div key={task.task_id} className="rounded-xl bg-[#0F1726] border border-[#253248] px-5 py-4">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div>
                        <p className="text-[14px] font-semibold text-[#F5F7FA]">{task.title}</p>
                        {task.description && <p className="text-[11px] text-[#667386] mt-0.5">{task.description}</p>}
                      </div>
                      <span className={`text-[11px] font-semibold ${
                        (task.status || "").toUpperCase() === "COMPLETED" ? "text-[#22C55E]" :
                        (task.status || "").toUpperCase() === "IN_PROGRESS" ? "text-[#3B82F6]" :
                        "text-[#F59E0B]"
                      }`}>{task.status}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-[10px] text-[#667386]">
                      <Zap size={10} className="text-[#8B5CF6]" />
                      <span>Priority {task.priority}</span>
                      {task.due_date && <><span className="text-[#253248]">·</span><span>Due {new Date(task.due_date).toLocaleDateString()}</span></>}
                    </div>
                  </div>
                ))}
              </div>
            )
          )}

          {activeTab === "Artifacts" && (
            artifacts.length === 0 ? (
              <div className="text-center py-16">
                <Package size={28} className="text-[#253248] mx-auto mb-3" />
                <p className="text-[13px] text-[#667386]">Ask the assistant to generate a document for this project</p>
              </div>
            ) : (
              <div className="space-y-2.5">
                {artifacts.map((art) => (
                  <div key={art.artifact_id} className="rounded-xl bg-[#0F1726] border border-[#253248] hover:border-[#2e3e57] transition-all group">
                    <div className="flex items-center gap-4 px-5 py-4">
                      <div className="w-10 h-10 rounded-xl bg-[#8B5CF6]/12 flex items-center justify-center flex-none">
                        <FileText size={18} className="text-[#8B5CF6]" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="text-[13px] font-semibold text-[#F5F7FA]">{art.name}</p>
                          <span className="text-[9px] bg-[#253248] text-[#9AA6B5] px-1.5 py-0.5 rounded font-bold">{art.artifact_type}</span>
                        </div>
                        <p className="text-[11px] text-[#667386]">{new Date(art.created_at).toLocaleString()}</p>
                      </div>
                      {art.artifact_id && (
                        <a href={`http://localhost:8000/api/artifacts/${art.artifact_id}/download`}
                          className="h-7 px-2.5 rounded-md text-[11px] text-[#9AA6B5] bg-[#141E2F] border border-[#253248] hover:text-[#F5F7FA] transition-all flex items-center gap-1">
                          <Download size={11} /> Download
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )
          )}

          {activeTab === "Approvals" && (
            approvals.length === 0 ? (
              <div className="text-center py-16">
                <AlertTriangle size={28} className="text-[#253248] mx-auto mb-3" />
                <p className="text-[13px] text-[#667386]">No approvals linked to this project yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {approvals.map((ap) => (
                  <div key={ap.id} className="rounded-xl bg-[#0F1726] border border-[#253248] px-5 py-4">
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <p className="text-[14px] font-semibold text-[#F5F7FA]">{ap.artifact_name || ap.approval_id}</p>
                          <span className="text-[9px] bg-[#253248] text-[#9AA6B5] px-1.5 py-0.5 rounded font-bold">{ap.artifact_type}</span>
                        </div>
                        <p className="text-[11px] text-[#667386]">{ap.approval_id} · Requested by {ap.requested_by_name || `User #${ap.requested_by}`}</p>
                      </div>
                      <span className={`text-[11px] font-semibold ${
                        ap.status.toUpperCase() === "PENDING" ? "text-[#F59E0B]" :
                        ap.status.toUpperCase() === "APPROVED" ? "text-[#22C55E]" : "text-[#EF4444]"
                      }`}>{ap.status}</span>
                    </div>
                    {ap.comments && <p className="text-[12px] text-[#9AA6B5] italic">{ap.comments}</p>}
                  </div>
                ))}
              </div>
            )
          )}
        </>
        )}
      </div>
    </div>
  );
}