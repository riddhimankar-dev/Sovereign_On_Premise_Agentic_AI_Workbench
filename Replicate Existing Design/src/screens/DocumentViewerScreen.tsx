import { ArrowLeft, FileText, ChevronLeft, ChevronRight, ZoomIn, ZoomOut, MessageSquare, Download, Check } from "lucide-react";

interface DocumentViewerScreenProps {
  onBack: () => void;
  onAskAI?: () => void;
}

const pages = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];

function MockDocumentPage({ page }: { page: number }) {
  const isFirstPage = page === 1;
  const isSeventhPage = page === 7;

  return (
    <div className="bg-white rounded-sm shadow-sm overflow-hidden" style={{ aspectRatio: "8.5/11", width: "100%" }}>
      <div className="h-full p-8 text-[#1a1a1a]">
        {isFirstPage && (
          <>
            <div className="text-center mb-8">
              <div className="text-xs font-semibold text-gray-400 tracking-widest mb-2">APEXPETRO ENERGY LIMITED</div>
              <div className="text-xs text-gray-400 mb-6">INSPECTION & INTEGRITY DEPARTMENT</div>
              <div className="h-px bg-gray-300 mb-6" />
              <h1 className="text-lg font-bold mb-2 text-gray-900">P-102 INSPECTION REPORT 2026</h1>
              <p className="text-sm text-gray-500 mb-1">Centrifugal Process Pump — CDU-4</p>
              <p className="text-sm text-gray-500 mb-6">Jamnagar Refinery Complex</p>
              <div className="inline-block bg-yellow-50 border border-yellow-300 text-yellow-800 text-xs font-semibold px-3 py-1 rounded">
                CONFIDENTIAL
              </div>
            </div>
            <div className="h-px bg-gray-200 mb-6" />
            <div className="space-y-2 text-xs text-gray-600">
              <div className="flex justify-between"><span>Inspection Date</span><span className="font-medium">2026-08-15</span></div>
              <div className="flex justify-between"><span>Inspector</span><span className="font-medium">Arjun Mehta</span></div>
              <div className="flex justify-between"><span>Asset ID</span><span className="font-medium">P-102</span></div>
              <div className="flex justify-between"><span>Classification</span><span className="font-medium text-yellow-700">CONFIDENTIAL</span></div>
            </div>
          </>
        )}
        {isSeventhPage && (
          <>
            <div className="text-xs font-semibold text-gray-400 mb-4">SECTION 3 — PRESSURE MEASUREMENTS</div>
            <h2 className="text-sm font-bold text-gray-900 mb-4">3.1 Operating Pressure Data</h2>
            <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
              <p className="text-xs font-semibold text-red-700 mb-1">LIMIT EXCEEDED</p>
              <p className="text-xs text-red-600">Current operating pressure of 42 bar exceeds maximum operating limit of 40 bar per SOP Section 7.2.</p>
            </div>
            <div className="space-y-2 mb-6">
              {[
                { param: "Operating Pressure", value: "42 bar", limit: "40 bar", status: "EXCEEDED" },
                { param: "Design Pressure", value: "50 bar", limit: "50 bar", status: "OK" },
                { param: "Suction Pressure", value: "3.2 bar", limit: "5 bar", status: "OK" },
              ].map(({ param, value, limit, status }) => (
                <div key={param} className="flex items-center justify-between text-xs border-b border-gray-100 pb-2">
                  <span className="text-gray-600 w-1/3">{param}</span>
                  <span className="font-semibold w-1/4 text-center">{value}</span>
                  <span className="text-gray-400 w-1/4 text-center">{limit}</span>
                  <span className={`font-semibold text-right w-1/4 ${status === "EXCEEDED" ? "text-red-600" : "text-green-600"}`}>{status}</span>
                </div>
              ))}
            </div>
            <div className="text-xs text-gray-500 space-y-2">
              <p>The pressure deviation of +2 bar above the operating limit requires engineering review per the applicable SOP before continued operation can be authorized.</p>
              <p>Historical comparison indicates a consistent upward trend in operating pressure over the past three inspection cycles (2024: 34 bar, 2025: 37 bar, 2026: 42 bar).</p>
            </div>
          </>
        )}
        {!isFirstPage && !isSeventhPage && (
          <div className="h-full flex items-center justify-center">
            <p className="text-xs text-gray-300">Page {page}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function DocumentViewerScreen({ onBack, onAskAI }: DocumentViewerScreenProps) {
  return (
    <div className="h-full flex flex-col bg-[#080D18]">
      {/* Header bar */}
      <div className="flex-none flex items-center gap-4 px-4 py-2.5 border-b border-[#253248] bg-[#0F1726]">
        <button onClick={onBack} className="flex items-center gap-1.5 text-[11px] text-[#667386] hover:text-[#9AA6B5] transition-colors">
          <ArrowLeft size={13} /> Files
        </button>
        <div className="flex items-center gap-2 flex-1">
          <FileText size={14} className="text-[#8B5CF6]" />
          <p className="text-[13px] font-medium text-[#F5F7FA]">P-102_Inspection_Report_2026.pdf</p>
          <span className="text-[9px] font-semibold text-[#F59E0B] bg-[#F59E0B]/8 px-1.5 py-0.5 rounded">CONFIDENTIAL</span>
          <span className="text-[9px] bg-[#22C55E]/10 text-[#22C55E] font-semibold px-1.5 py-0.5 rounded flex items-center gap-1">
            <Check size={9} /> Indexed
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button className="w-7 h-7 rounded-md flex items-center justify-center text-[#667386] hover:text-[#9AA6B5] hover:bg-[#141E2F] transition-all">
            <ZoomOut size={13} />
          </button>
          <span className="text-[11px] font-mono text-[#667386] w-10 text-center">100%</span>
          <button className="w-7 h-7 rounded-md flex items-center justify-center text-[#667386] hover:text-[#9AA6B5] hover:bg-[#141E2F] transition-all">
            <ZoomIn size={13} />
          </button>
        </div>
        <button className="w-7 h-7 rounded-md flex items-center justify-center text-[#667386] hover:text-[#9AA6B5] hover:bg-[#141E2F] transition-all">
          <Download size={13} />
        </button>
      </div>

      {/* Three-panel layout */}
      <div className="flex-1 flex min-h-0 overflow-hidden">
        {/* Left: page thumbnails */}
        <div className="w-[130px] flex-none border-r border-[#253248] bg-[#0F1726] overflow-y-auto">
          <div className="p-2 space-y-1.5">
            {pages.map((p) => (
              <button
                key={p}
                className={`w-full rounded-md overflow-hidden border-2 transition-all ${
                  p === 7 ? "border-[#8B5CF6]" : "border-transparent hover:border-[#253248]"
                }`}
              >
                <div className="bg-white rounded-sm" style={{ aspectRatio: "8.5/11" }}>
                  <div className="h-full flex items-center justify-center">
                    {p === 1 ? (
                      <div className="text-center px-2">
                        <div className="text-[5px] font-bold text-gray-700 leading-tight">P-102 INSPECTION REPORT 2026</div>
                        <div className="h-px bg-gray-300 my-1" />
                        <div className="text-[4px] text-gray-400">CONFIDENTIAL</div>
                      </div>
                    ) : (
                      <span className="text-[7px] text-gray-300">Pg {p}</span>
                    )}
                  </div>
                </div>
                <p className={`text-[9px] text-center py-0.5 ${p === 7 ? "text-[#8B5CF6]" : "text-[#667386]"}`}>{p}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Center: document */}
        <div className="flex-1 min-w-0 overflow-y-auto bg-[#141E2F] flex flex-col items-center py-6 px-8 gap-4">
          <div style={{ width: "min(560px, 100%)" }}>
            <MockDocumentPage page={7} />
          </div>
          <div className="flex items-center gap-3 mt-2">
            <button className="w-7 h-7 rounded-md bg-[#0F1726] border border-[#253248] flex items-center justify-center text-[#667386] hover:text-[#F5F7FA] transition-all">
              <ChevronLeft size={13} />
            </button>
            <p className="text-[11px] text-[#9AA6B5]">Page 7 of 12</p>
            <button className="w-7 h-7 rounded-md bg-[#0F1726] border border-[#253248] flex items-center justify-center text-[#667386] hover:text-[#F5F7FA] transition-all">
              <ChevronRight size={13} />
            </button>
          </div>
        </div>

        {/* Right: document info + AI data */}
        <div className="w-[264px] flex-none border-l border-[#253248] bg-[#0F1726] overflow-y-auto">
          <div className="divide-y divide-[#253248]">
            {/* Document info */}
            <div className="px-4 py-4">
              <p className="text-[9px] font-semibold tracking-widest text-[#667386] uppercase mb-3">Document Information</p>
              <div className="space-y-2">
                {[
                  { label: "Title", value: "P-102 Inspection Report 2026" },
                  { label: "Type", value: "Inspection Report" },
                  { label: "Classification", value: "CONFIDENTIAL", highlight: "warning" },
                  { label: "Asset", value: "P-102" },
                  { label: "Department", value: "Inspection & Integrity" },
                  { label: "Date", value: "2026-08-15" },
                  { label: "Status", value: "Indexed", highlight: "success" },
                ].map(({ label, value, highlight }) => (
                  <div key={label} className="flex items-start justify-between gap-2">
                    <p className="text-[10px] text-[#667386] flex-none">{label}</p>
                    <p className={`text-[11px] text-right leading-snug ${
                      highlight === "warning" ? "text-[#F59E0B] font-semibold" :
                      highlight === "success" ? "text-[#22C55E] font-semibold" :
                      "text-[#9AA6B5]"
                    }`}>{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* AI extracted data */}
            <div className="px-4 py-4">
              <p className="text-[9px] font-semibold tracking-widest text-[#667386] uppercase mb-3">AI Extracted Data</p>
              <div className="space-y-2.5">
                {[
                  { param: "Pressure", value: "42 bar", status: "critical" },
                  { param: "Temperature", value: "190°C", status: "normal" },
                  { param: "Corrosion", value: "3.8 mm", status: "warning" },
                  { param: "Vibration", value: "7.2 mm/s", status: "warning" },
                ].map(({ param, value, status }) => (
                  <div key={param} className="flex items-center justify-between">
                    <p className="text-[11px] text-[#9AA6B5]">{param}</p>
                    <p className={`text-[12px] font-semibold font-mono ${
                      status === "critical" ? "text-[#EF4444]" :
                      status === "warning" ? "text-[#F59E0B]" :
                      "text-[#9AA6B5]"
                    }`}>{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Ask AI button */}
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
