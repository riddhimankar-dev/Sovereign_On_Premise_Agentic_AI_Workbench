import { useState } from "react";
import {
  ArrowLeft, AlertTriangle, Clock, FileText, Package, ClipboardCheck,
  CheckSquare, Zap, ExternalLink, Eye, Download, Check, ChevronRight,
  FileSpreadsheet,
} from "lucide-react";

interface ProjectDetailScreenProps {
  onBack: () => void;
}

const tabs = ["Overview", "Files", "AI Tasks", "Sources", "Artifacts", "Approvals"];

const projectFiles = [
  { name: "P-102_Inspection_Report_2026.pdf", type: "PDF", size: "4.2 MB", classification: "CONFIDENTIAL", status: "Indexed", icon: FileText, iconColor: "text-[#8B5CF6]", iconBg: "bg-[#8B5CF6]/12" },
  { name: "P-102_Equipment_Photo.jpg", type: "IMAGE", size: "2.8 MB", classification: "CONFIDENTIAL", status: "Indexed", icon: FileText, iconColor: "text-[#14B8A6]", iconBg: "bg-[#14B8A6]/12" },
  { name: "P-102_Measurements.xlsx", type: "XLSX", size: "680 KB", classification: "INTERNAL", status: "Indexed", icon: FileSpreadsheet, iconColor: "text-[#22C55E]", iconBg: "bg-[#22C55E]/12" },
  { name: "Pump_Inspection_SOP.pdf", type: "PDF", size: "1.1 MB", classification: "CONFIDENTIAL", status: "Indexed", icon: FileText, iconColor: "text-[#8B5CF6]", iconBg: "bg-[#8B5CF6]/12" },
  { name: "P-102_Inspection_Report_2025.pdf", type: "PDF", size: "3.9 MB", classification: "CONFIDENTIAL", status: "Indexed", icon: FileText, iconColor: "text-[#8B5CF6]", iconBg: "bg-[#8B5CF6]/12" },
  { name: "Vendor_Inspection_Report_2026.pdf", type: "PDF", size: "6.1 MB", classification: "CONFIDENTIAL", status: "Indexed", icon: FileText, iconColor: "text-[#8B5CF6]", iconBg: "bg-[#8B5CF6]/12" },
];

const projectArtifacts = [
  { name: "Approval_Note_P-102_2026", ext: "DOCX", status: "Awaiting Approval", statusColor: "text-[#F59E0B]", created: "Today, 09:42", agent: "Inspection Analyst" },
  { name: "Risk_Assessment_P-102", ext: "XLSX", status: "Verified", statusColor: "text-[#22C55E]", created: "Today, 09:40", agent: "Inspection Analyst" },
];

const projectTasks = [
  { name: "P-102 Inspection Analysis", status: "Awaiting Approval", statusColor: "text-[#F59E0B]", steps: "10/12", agent: "Inspection Analyst", created: "Today, 09:41" },
];

const projectSources = [
  { num: "01", title: "P-102 Inspection Report 2026", section: "Page 7", classification: "CONFIDENTIAL", relevance: 98 },
  { num: "02", title: "Pump Inspection SOP v3.2", section: "Section 7.2", classification: "CONFIDENTIAL", relevance: 95 },
  { num: "03", title: "P-102 Inspection Report 2025", section: "Page 4", classification: "CONFIDENTIAL", relevance: 87 },
  { num: "04", title: "P-102 Maintenance History", section: "2025-10-12", classification: "INTERNAL", relevance: 82 },
  { num: "05", title: "P-102 Equipment Datasheet", section: "Section 3", classification: "INTERNAL", relevance: 79 },
  { num: "06", title: "Corrosion Assessment SOP", section: "Section 4.1", classification: "CONFIDENTIAL", relevance: 74 },
];

function OverviewTab() {
  return (
    <div className="space-y-5">
      {/* Key metrics */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Operating Pressure", value: "42 bar", limit: "Limit: 40 bar", status: "critical", statusText: "Exceeded" },
          { label: "Corrosion Rate", value: "3.8 mm", limit: "Assessment required", status: "warning", statusText: "Engineering review" },
          { label: "Vibration", value: "7.2 mm/s", limit: ">7 mm/s threshold", status: "warning", statusText: "High concern" },
        ].map(({ label, value, limit, status, statusText }) => (
          <div key={label} className={`rounded-xl border p-4 ${
            status === "critical" ? "bg-[#EF4444]/6 border-[#EF4444]/20" : "bg-[#F59E0B]/6 border-[#F59E0B]/20"
          }`}>
            <p className="text-[10px] font-semibold tracking-widest text-[#667386] uppercase mb-2">{label}</p>
            <p className={`text-[24px] font-semibold font-mono leading-none ${status === "critical" ? "text-[#EF4444]" : "text-[#F59E0B]"}`}>{value}</p>
            <p className="text-[10px] text-[#667386] mt-1.5">{limit}</p>
            <p className={`text-[10px] font-semibold mt-1 ${status === "critical" ? "text-[#EF4444]" : "text-[#F59E0B]"}`}>{statusText}</p>
          </div>
        ))}
      </div>

      {/* Historical trend */}
      <div className="rounded-xl bg-[#0F1726] border border-[#253248] p-5">
        <p className="text-[12px] font-semibold text-[#F5F7FA] mb-1">Historical Trend</p>
        <p className="text-[10px] text-[#667386] mb-4">P-102 operating parameters 2024–2026</p>
        <div className="grid grid-cols-3 gap-4">
          {[
            { year: "2024", pressure: "34 bar", corrosion: "1.2 mm", vibration: "4.1 mm/s", status: "normal" },
            { year: "2025", pressure: "37 bar", corrosion: "2.4 mm", vibration: "5.3 mm/s", status: "monitor" },
            { year: "2026", pressure: "42 bar", corrosion: "3.8 mm", vibration: "7.2 mm/s", status: "critical" },
          ].map(({ year, pressure, corrosion, vibration, status }) => (
            <div key={year} className={`rounded-lg border p-3 ${
              status === "critical" ? "bg-[#EF4444]/6 border-[#EF4444]/15" :
              status === "monitor" ? "bg-[#F59E0B]/6 border-[#F59E0B]/15" :
              "bg-[#141E2F] border-[#253248]"
            }`}>
              <p className={`text-[13px] font-semibold mb-2 ${
                status === "critical" ? "text-[#EF4444]" : status === "monitor" ? "text-[#F59E0B]" : "text-[#22C55E]"
              }`}>{year}</p>
              <div className="space-y-1">
                <p className="text-[11px] text-[#9AA6B5] font-mono">{pressure}</p>
                <p className="text-[11px] text-[#9AA6B5] font-mono">{corrosion}</p>
                <p className="text-[11px] text-[#9AA6B5] font-mono">{vibration}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendation */}
      <div className="rounded-xl bg-[#F59E0B]/6 border border-[#F59E0B]/25 p-5">
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle size={14} className="text-[#F59E0B]" />
          <p className="text-[11px] font-semibold text-[#F59E0B] uppercase tracking-wide">AI Recommendation</p>
        </div>
        <p className="text-[13px] text-[#F5F7FA] font-medium leading-relaxed">
          Engineering integrity review is recommended before continued operation under current conditions.
        </p>
        <p className="text-[11px] text-[#9AA6B5] mt-2">AI-generated · Requires authorized human review before action</p>
      </div>

      {/* Project metadata */}
      <div className="rounded-xl bg-[#0F1726] border border-[#253248] p-5">
        <p className="text-[11px] font-semibold text-[#667386] uppercase tracking-widest mb-3">Project Information</p>
        <div className="grid grid-cols-2 gap-y-3 gap-x-8">
          {[
            { label: "Company", value: "ApexPetro Energy Limited" },
            { label: "Facility", value: "Jamnagar Refinery Complex" },
            { label: "Department", value: "Inspection & Integrity" },
            { label: "Unit", value: "CDU-4" },
            { label: "Asset", value: "P-102 (Centrifugal Pump)" },
            { label: "Service", value: "Crude Transfer" },
            { label: "Criticality", value: "HIGH" },
            { label: "Classification", value: "CONFIDENTIAL" },
            { label: "Created", value: "Today, 09:41" },
            { label: "Last Activity", value: "2 min ago" },
          ].map(({ label, value }) => (
            <div key={label} className="flex items-start justify-between gap-2">
              <p className="text-[11px] text-[#667386] flex-none">{label}</p>
              <p className="text-[11px] text-[#9AA6B5] text-right leading-snug">{value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ProjectDetailScreen({ onBack }: ProjectDetailScreenProps) {
  const [activeTab, setActiveTab] = useState("Overview");

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
              {/* Context breadcrumb */}
              <div className="flex items-center gap-1.5 text-[10px] text-[#667386] mb-2 flex-wrap">
                <span>ApexPetro Energy Limited</span>
                <ChevronRight size={10} />
                <span>Jamnagar Refinery Complex</span>
                <ChevronRight size={10} />
                <span>CDU-4</span>
                <ChevronRight size={10} />
                <span className="text-[#9AA6B5] font-medium">P-102</span>
              </div>

              <h1 className="text-[22px] font-semibold text-[#F5F7FA]">P-102 Equipment Integrity Review</h1>
              <p className="text-[12px] text-[#667386] mt-0.5">Centrifugal Process Pump · Crude Transfer Service · Inspection & Integrity</p>
            </div>

            <div className="flex items-center gap-2 flex-none">
              <span className="flex items-center gap-1.5 text-[11px] font-bold text-[#EF4444] bg-[#EF4444]/10 border border-[#EF4444]/20 px-2.5 py-1 rounded-lg">
                <AlertTriangle size={12} />
                HIGH RISK
              </span>
              <span className="text-[11px] font-semibold text-[#F59E0B] bg-[#F59E0B]/10 border border-[#F59E0B]/20 px-2.5 py-1 rounded-lg">
                Awaiting Approval
              </span>
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
                {tab === "Approvals" && <span className="ml-1.5 text-[9px] bg-[#F59E0B]/20 text-[#F59E0B] px-1 py-0.5 rounded-full">1</span>}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-6">
        {activeTab === "Overview" && <OverviewTab />}

        {activeTab === "Files" && (
          <div className="space-y-2">
            {projectFiles.map((file) => {
              const Icon = file.icon;
              return (
                <div key={file.name} className="flex items-center gap-4 px-5 py-3.5 rounded-xl bg-[#0F1726] border border-[#253248] hover:border-[#2e3e57] cursor-pointer group transition-all">
                  <div className={`w-9 h-9 rounded-lg ${file.iconBg} flex items-center justify-center flex-none`}>
                    <Icon size={16} className={file.iconColor} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] font-medium text-[#F5F7FA] truncate">{file.name}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[9px] bg-[#253248] text-[#9AA6B5] px-1.5 py-0.5 rounded font-bold">{file.type}</span>
                      <span className="text-[10px] text-[#667386]">{file.size}</span>
                      <span className="text-[9px] text-[#F59E0B] font-semibold">{file.classification}</span>
                    </div>
                  </div>
                  <span className="flex items-center gap-1 text-[10px] text-[#22C55E]">
                    <Check size={10} /> {file.status}
                  </span>
                  <ChevronRight size={13} className="text-[#253248] group-hover:text-[#667386] transition-colors flex-none" />
                </div>
              );
            })}
          </div>
        )}

        {activeTab === "AI Tasks" && (
          <div className="space-y-3">
            {projectTasks.map((task) => (
              <div key={task.name} className="rounded-xl bg-[#0F1726] border border-[#253248] px-5 py-4">
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div>
                    <p className="text-[14px] font-semibold text-[#F5F7FA]">{task.name}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <Zap size={11} className="text-[#8B5CF6]" />
                      <p className="text-[11px] text-[#667386]">{task.agent}</p>
                      <span className="text-[#253248]">·</span>
                      <p className="text-[11px] text-[#667386]">{task.created}</p>
                    </div>
                  </div>
                  <span className={`text-[11px] font-semibold ${task.statusColor}`}>{task.status}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-1 bg-[#253248] rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-[#8B5CF6] to-[#14B8A6] rounded-full" style={{ width: "83%" }} />
                  </div>
                  <span className="text-[10px] font-mono text-[#667386]">{task.steps}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === "Sources" && (
          <div className="space-y-2">
            {projectSources.map((src) => (
              <div key={src.num} className="flex items-start gap-3 px-5 py-3.5 rounded-xl bg-[#0F1726] border border-[#253248] hover:border-[#2e3e57] cursor-pointer group transition-all">
                <span className="text-[10px] font-mono font-semibold text-[#667386] w-5 flex-none mt-0.5">{src.num}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-[13px] font-medium text-[#F5F7FA]">{src.title}</p>
                  <p className="text-[10px] text-[#9AA6B5] mt-0.5">{src.section}</p>
                </div>
                <div className="flex items-center gap-2 flex-none">
                  <span className="text-[9px] text-[#F59E0B] font-semibold">{src.classification}</span>
                  <div className="w-8 h-1 bg-[#253248] rounded-full overflow-hidden">
                    <div className="h-full bg-[#8B5CF6] rounded-full" style={{ width: `${src.relevance}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === "Artifacts" && (
          <div className="space-y-2.5">
            {projectArtifacts.map((art) => (
              <div key={art.name} className="rounded-xl bg-[#0F1726] border border-[#253248] hover:border-[#2e3e57] transition-all group">
                <div className="flex items-center gap-4 px-5 py-4">
                  <div className="w-10 h-10 rounded-xl bg-[#8B5CF6]/12 flex items-center justify-center flex-none">
                    <FileText size={18} className="text-[#8B5CF6]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-[13px] font-semibold text-[#F5F7FA]">{art.name}</p>
                      <span className="text-[9px] bg-[#253248] text-[#9AA6B5] px-1.5 py-0.5 rounded font-bold">{art.ext}</span>
                    </div>
                    <p className="text-[11px] text-[#667386]">{art.agent} · {art.created}</p>
                  </div>
                  <p className={`text-[11px] font-medium ${art.statusColor} flex-none`}>{art.status}</p>
                  <div className="flex gap-1.5 flex-none">
                    <button className="h-7 px-2.5 rounded-md text-[11px] text-[#9AA6B5] bg-[#141E2F] border border-[#253248] hover:text-[#F5F7FA] transition-all flex items-center gap-1">
                      <Eye size={11} /> Preview
                    </button>
                    <button className="h-7 px-2.5 rounded-md text-[11px] text-[#9AA6B5] bg-[#141E2F] border border-[#253248] hover:text-[#F5F7FA] transition-all flex items-center gap-1">
                      <Download size={11} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === "Approvals" && (
          <div className="rounded-xl bg-[#F59E0B]/6 border border-[#F59E0B]/30 overflow-hidden">
            <div className="px-5 py-3 border-b border-[#F59E0B]/20 flex items-center gap-2">
              <AlertTriangle size={14} className="text-[#F59E0B]" />
              <p className="text-[12px] font-semibold text-[#F59E0B]">Human Review Required</p>
            </div>
            <div className="px-5 py-5">
              <p className="text-[14px] font-semibold text-[#F5F7FA] mb-4">P-102 Equipment Integrity Review</p>
              <div className="grid grid-cols-4 gap-3 mb-4">
                {[
                  { label: "Risk Level", value: "HIGH", color: "text-[#EF4444]" },
                  { label: "Evidence", value: "6 sources", color: "text-[#9AA6B5]" },
                  { label: "Verification", value: "PASSED", color: "text-[#22C55E]" },
                  { label: "Artifact", value: "Approval_Note.docx", color: "text-[#9AA6B5]" },
                ].map(({ label, value, color }) => (
                  <div key={label} className="rounded-lg bg-[#141E2F] border border-[#253248] p-2.5">
                    <p className="text-[9px] text-[#667386] mb-1">{label}</p>
                    <p className={`text-[12px] font-semibold ${color}`}>{value}</p>
                  </div>
                ))}
              </div>
              <p className="text-[13px] text-[#F5F7FA] italic mb-4 leading-relaxed">
                "Engineering integrity review is recommended before continued operation under current conditions."
              </p>
              <p className="text-[11px] text-[#667386] mb-4">AI-generated recommendation · Requires authorized human review</p>
              <div className="flex gap-2">
                <button className="flex-1 h-9 rounded-lg border border-[#253248] text-[12px] text-[#9AA6B5] hover:bg-[#182337] transition-all flex items-center justify-center gap-2">
                  <Eye size={13} /> Review Evidence
                </button>
                <button className="h-9 px-5 rounded-lg border border-[#EF4444]/30 text-[12px] text-[#EF4444] hover:bg-[#EF4444]/10 transition-all">Reject</button>
                <button className="h-9 px-6 rounded-lg bg-[#22C55E] text-[12px] text-white font-semibold hover:bg-[#16A34A] transition-all">Approve</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
