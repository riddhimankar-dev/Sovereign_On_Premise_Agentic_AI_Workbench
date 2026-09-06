import { ArrowLeft, FileText, ZoomIn, ZoomOut, MessageSquare, Download, Check } from "lucide-react";
import { Document } from "../services/api";

interface DocumentViewerScreenProps {
  document: Document | null;
  onBack: () => void;
  onAskAI?: () => void;
}

function statusBadge(status: string) {
  const s = status.toUpperCase();
  if (s === "READY" || s === "INDEXED") return { text: "bg-[#22C55E]/10 text-[#22C55E]", icon: <Check size={9} /> };
  if (s === "FAILED") return { text: "bg-[#EF4444]/10 text-[#EF4444]", icon: <span className="text-[9px]">!</span> };
  return { text: "bg-[#F59E0B]/10 text-[#F59E0B]", icon: <span className="text-[9px]">…</span> };
}

export default function DocumentViewerScreen({ document: doc, onBack, onAskAI }: DocumentViewerScreenProps) {
  if (!doc) {
    return (
      <div className="h-full flex flex-col bg-[#080D18] items-center justify-center">
        <p className="text-[12px] text-[#667386]">No document selected.</p>
        <button onClick={onBack} className="mt-4 text-[11px] text-[#8B5CF6] hover:underline">Back to Files</button>
      </div>
    );
  }

  const badge = statusBadge(doc.status);
  const classificationIsConf = (doc.classification || "").toUpperCase() === "CONFIDENTIAL";
  const pageCount = doc.page_count ?? 1;

  return (
    <div className="h-full flex flex-col bg-[#080D18]">
      {/* Header bar */}
      <div className="flex-none flex items-center gap-4 px-4 py-2.5 border-b border-[#253248] bg-[#0F1726]">
        <button onClick={onBack} className="flex items-center gap-1.5 text-[11px] text-[#667386] hover:text-[#9AA6B5] transition-colors">
          <ArrowLeft size={13} /> Files
        </button>
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <FileText size={14} className="text-[#8B5CF6] flex-none" />
          <p className="text-[13px] font-medium text-[#F5F7FA] truncate">{doc.file_name}</p>
          <span className="text-[9px] font-bold bg-[#253248] text-[#9AA6B5] px-1.5 py-0.5 rounded flex-none">{doc.file_type}</span>
          {classificationIsConf && (
            <span className="text-[9px] font-semibold text-[#F59E0B] bg-[#F59E0B]/8 px-1.5 py-0.5 rounded flex-none">CONFIDENTIAL</span>
          )}
          <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded flex items-center gap-1 flex-none ${badge.text}`}>
            {badge.icon} {doc.status}
          </span>
        </div>
        <div className="flex items-center gap-1 flex-none">
          <button className="w-7 h-7 rounded-md flex items-center justify-center text-[#667386] hover:text-[#9AA6B5] hover:bg-[#141E2F] transition-all">
            <ZoomOut size={13} />
          </button>
          <span className="text-[11px] font-mono text-[#667386] w-10 text-center">100%</span>
          <button className="w-7 h-7 rounded-md flex items-center justify-center text-[#667386] hover:text-[#9AA6B5] hover:bg-[#141E2F] transition-all">
            <ZoomIn size={13} />
          </button>
        </div>
      </div>

      {/* Main layout */}
      <div className="flex-1 flex min-h-0 overflow-hidden">
        {/* Left: thumbnail list */}
        <div className="w-[110px] flex-none border-r border-[#253248] bg-[#0F1726] overflow-y-auto">
          <div className="p-2 space-y-1.5">
            {Array.from({ length: Math.min(pageCount, 20) }, (_, i) => i + 1).map((p) => (
              <div
                key={p}
                className={`w-full rounded-md overflow-hidden border-2 transition-all ${
                  p === 1 ? "border-[#8B5CF6]" : "border-transparent hover:border-[#253248]"
                }`}
              >
                <div className="bg-white rounded-sm" style={{ aspectRatio: "8.5/11" }}>
                  <div className="h-full flex items-center justify-center">
                    {p === 1 ? (
                      <div className="text-center px-2">
                        <div className="text-[5px] font-bold text-gray-700 leading-tight">{doc.file_name.slice(0, 28)}</div>
                        <div className="h-px bg-gray-300 my-1" />
                        <div className="text-[4px] text-gray-400">{doc.classification}</div>
                      </div>
                    ) : (
                      <span className="text-[7px] text-gray-300">Pg {p}</span>
                    )}
                  </div>
                </div>
                <p className={`text-[9px] text-center py-0.5 ${p === 1 ? "text-[#8B5CF6]" : "text-[#667386]"}`}>{p}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Center: document placeholder */}
        <div className="flex-1 min-w-0 overflow-y-auto bg-[#141E2F] flex flex-col items-center justify-center py-6 px-8 gap-4">
          <div
            style={{ width: "min(480px, 100%)" }}
            className="bg-white rounded-sm shadow-sm p-10 text-center"
          >
            <FileText size={28} className="text-[#8B5CF6] mx-auto mb-3" />
            <p className="text-[13px] font-semibold text-gray-700 mb-2">{doc.file_name}</p>
            <p className="text-[11px] text-gray-400 mb-4">
              Full document preview is rendered locally via the knowledge index.<br />
              Use the <strong>Ask AI</strong> panel or chat to query this document's contents.
            </p>
            <div className="inline-block text-[9px] font-semibold px-3 py-1 rounded border text-gray-500 bg-gray-50 border-gray-200">
              {doc.file_type.toUpperCase()} · {doc.page_count != null ? `${doc.page_count} pages` : "Indexed"}
            </div>
          </div>
          <p className="text-[10px] text-[#667386]">Page 1 of {pageCount}</p>
        </div>

        {/* Right: document info */}
        <div className="w-[264px] flex-none border-l border-[#253248] bg-[#0F1726] overflow-y-auto">
          <div className="divide-y divide-[#253248]">
            <div className="px-4 py-4">
              <p className="text-[9px] font-semibold tracking-widest text-[#667386] uppercase mb-3">Document Information</p>
              <div className="space-y-2">
                {[
                  { label: "Title",   value: doc.file_name },
                  { label: "Type",    value: doc.file_type.toUpperCase() },
                  { label: "Classification", value: doc.classification, color: classificationIsConf ? "text-[#F59E0B] font-semibold" : "text-[#9AA6B5]" },
                  { label: "Status",  value: doc.status, color: (doc.status || "").toUpperCase() === "READY" ? "text-[#22C55E] font-semibold" : "text-[#9AA6B5]" },
                  { label: "Pages",   value: doc.page_count != null ? String(doc.page_count) : "—" },
                  { label: "Size",    value: `${(doc.file_size / 1024 / 1024).toFixed(1)} MB` },
                  { label: "Uploaded", value: doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : "—" },
                  { label: "Indexed", value: doc.indexed_at ? new Date(doc.indexed_at).toLocaleDateString() : "Not yet" },
                  { label: "Document ID", value: doc.document_id.slice(0, 12) + "…" },
                ].map(({ label, value, color }) => (
                  <div key={label} className="flex items-start justify-between gap-2">
                    <p className="text-[10px] text-[#667386] flex-none">{label}</p>
                    <p className={`text-[11px] text-right leading-snug truncate ${color || "text-[#9AA6B5]"}`}>{value}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="px-4 py-4">
              <p className="text-[9px] font-semibold tracking-widest text-[#667386] uppercase mb-3">AI Extracted Data</p>
              <p className="text-[11px] text-[#667386] italic leading-relaxed">
                Use the chat to query this document. The RAG index serves all extracted content — answers are grounded in the actual document, not mocked summaries.
              </p>
            </div>

            <div className="px-4 py-4">
              <button
                onClick={onAskAI}
                className="w-full h-9 rounded-lg bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-[12px] font-semibold transition-colors flex items-center justify-center gap-2 shadow-lg shadow-[#8B5CF6]/20"
              >
                <MessageSquare size={13} />
                Ask AI about this document
              </button>
              <p className="text-[10px] text-[#667386] text-center mt-2 leading-relaxed">
                Start a conversation using this document as context.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
