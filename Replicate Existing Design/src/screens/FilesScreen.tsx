import { useState, useEffect, useRef } from "react";
import { FileText, FileSpreadsheet, ImageIcon, Upload, Check, Loader, ChevronRight, Search, Filter } from "lucide-react";
import { api, Document } from "../services/api";

const typeBadge: Record<string, { icon: typeof FileText; iconColor: string; iconBg: string }> = {
  PDF: { icon: FileText, iconColor: "text-[#8B5CF6]", iconBg: "bg-[#8B5CF6]/12" },
  jpg: { icon: ImageIcon, iconColor: "text-[#14B8A6]", iconBg: "bg-[#14B8A6]/12" },
  png: { icon: ImageIcon, iconColor: "text-[#14B8A6]", iconBg: "bg-[#14B8A6]/12" },
  xlsx: { icon: FileSpreadsheet, iconColor: "text-[#22C55E]", iconBg: "bg-[#22C55E]/12" },
  docx: { icon: FileText, iconColor: "text-[#3B82F6]", iconBg: "bg-[#3B82F6]/12" },
};

function getTypeBadge(ft: string) {
  return typeBadge[ft] || { icon: FileText, iconColor: "text-[#667386]", iconBg: "bg-[#667386]/12" };
}

const statusColors: Record<string, { text: string; bg: string }> = {
  READY: { text: "text-[#22C55E]", bg: "bg-[#22C55E]/10" },
  INDEXED: { text: "text-[#22C55E]", bg: "bg-[#22C55E]/10" },
  PROCESSING: { text: "text-[#3B82F6]", bg: "bg-[#3B82F6]/10" },
  UPLOADING: { text: "text-[#3B82F6]", bg: "bg-[#3B82F6]/10" },
  ERROR: { text: "text-[#EF4444]", bg: "bg-[#EF4444]/10" },
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FilesScreen({ onSelectFile }: { onSelectFile?: (doc: Document) => void }) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [query, setQuery] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocs = () => {
    setLoading(true);
    setError(null);
    api.documents.list()
      .then(res => { setDocuments(res.documents); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  };

  useEffect(() => { fetchDocs(); }, []);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      await api.documents.upload(file, { classification: "CONFIDENTIAL" });
      fetchDocs();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleUpload(file);
  };

  const filtered = documents.filter(f => f.file_name.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      <div className="max-w-4xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h1 className="text-[22px] font-semibold text-[#F5F7FA]">Files</h1>
            <p className="text-[12px] text-[#667386] mt-0.5">Uploaded documents · ApexPetro Energy Limited</p>
          </div>
        </div>

        <div
          className={`rounded-xl border-2 border-dashed p-6 mb-5 transition-all text-center ${
            dragOver
              ? "border-[#8B5CF6] bg-[#8B5CF6]/8"
              : "border-[#253248] hover:border-[#2e3e57] hover:bg-[#0F1726]/50"
          }`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          style={{ cursor: "pointer" }}
        >
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".pdf,.docx,.xlsx,.pptx,.png,.jpg,.jpeg,.tiff"
            onChange={handleFileInput}
          />
          <Upload size={20} className={`mx-auto mb-2 ${dragOver || uploading ? "text-[#8B5CF6]" : "text-[#667386]"}`} />
          {uploading ? (
            <p className="text-[13px] font-medium text-[#8B5CF6] mb-1">Uploading...</p>
          ) : (
            <>
              <p className="text-[13px] font-medium text-[#F5F7FA] mb-1">Drop files here or click to upload</p>
              <p className="text-[11px] text-[#667386]">PDF, DOCX, XLSX, PPTX, PNG, JPG, TIFF</p>
            </>
          )}
          <div className="flex items-center gap-2 justify-center mt-3 flex-wrap">
            {["CONFIDENTIAL", "INTERNAL"].map((cls) => (
              <span key={cls} className="text-[9px] font-semibold text-[#F59E0B] bg-[#F59E0B]/8 px-1.5 py-0.5 rounded">
                Auto-classified as {cls}
              </span>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2 mb-4">
          <div className="flex-1 flex items-center gap-2 px-3 h-9 rounded-lg bg-[#0F1726] border border-[#253248] focus-within:border-[#8B5CF6]/40 transition-colors">
            <Search size={13} className="text-[#667386]" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search files..."
              className="flex-1 bg-transparent text-[13px] text-[#F5F7FA] placeholder-[#667386] outline-none"
            />
          </div>
          <button className="h-9 px-3 rounded-lg bg-[#0F1726] border border-[#253248] text-[#667386] hover:text-[#9AA6B5] transition-colors flex items-center gap-1.5 text-[11px]">
            <Filter size={12} /> Filter
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader size={24} className="text-[#8B5CF6] animate-spin" />
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <p className="text-[13px] text-[#EF4444]">{error}</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20">
            <FileText size={32} className="text-[#253248] mx-auto mb-3" />
            <p className="text-[13px] text-[#667386]">No documents uploaded yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((doc) => {
              const badge = getTypeBadge(doc.file_type);
              const Icon = badge.icon;
              const sc = statusColors[doc.status] || statusColors.READY;
              const isProcessing = doc.status === "PROCESSING" || doc.status === "UPLOADING";
              return (
                <div key={doc.document_id} onClick={() => onSelectFile?.(doc)}
                  className="rounded-xl bg-[#0F1726] border border-[#253248] hover:border-[#2e3e57] transition-all cursor-pointer group">
                  <div className="flex items-center gap-4 px-5 py-3.5">
                    <div className={`w-9 h-9 rounded-lg ${badge.iconBg} flex items-center justify-center flex-none`}>
                      <Icon size={16} className={badge.iconColor} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <p className="text-[13px] font-medium text-[#F5F7FA] truncate">{doc.file_name}</p>
                        <span className="text-[9px] font-bold bg-[#253248] text-[#9AA6B5] px-1.5 py-0.5 rounded flex-none">{doc.file_type}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[10px] text-[#667386]">{formatFileSize(doc.file_size)}</span>
                        {doc.page_count != null && doc.page_count > 1 && <span className="text-[10px] text-[#667386]">{doc.page_count} pages</span>}
                        <span className="text-[9px] font-semibold text-[#F59E0B] bg-[#F59E0B]/8 px-1.5 py-0.5 rounded">{doc.classification}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 flex-none">
                      <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full ${sc.bg}`}>
                        {isProcessing ? (
                          <Loader size={10} className={`${sc.text} animate-spin`} />
                        ) : (
                          <Check size={10} className={sc.text} />
                        )}
                        <span className={`text-[10px] font-semibold ${sc.text}`}>{doc.status}</span>
                      </div>
                      <ChevronRight size={13} className="text-[#253248] group-hover:text-[#667386] transition-colors" />
                    </div>
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
