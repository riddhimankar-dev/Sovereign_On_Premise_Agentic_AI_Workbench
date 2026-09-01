import { useState, useEffect, useCallback } from "react";
import { Search, BookOpen, FileText, ChevronRight, Filter, Loader2, AlertTriangle } from "lucide-react";
import { api, KnowledgeSearchResult } from "../services/api";

const filterTags = ["All", "SOP", "Manual", "Policy", "Inspection", "Maintenance", "Asset", "Historical", "Vendor"];

const typeColors: Record<string, string> = {
  SOP: "text-[#8B5CF6] bg-[#8B5CF6]/12",
  Asset: "text-[#3B82F6] bg-[#3B82F6]/12",
  Inspection: "text-[#14B8A6] bg-[#14B8A6]/12",
  Historical: "text-[#9AA6B5] bg-[#253248]",
  Manual: "text-[#F59E0B] bg-[#F59E0B]/12",
  Policy: "text-[#EF4444] bg-[#EF4444]/12",
  Maintenance: "text-[#22C55E] bg-[#22C55E]/12",
  Vendor: "text-[#A78BFA] bg-[#A78BFA]/12",
};

function inferType(meta: Record<string, any> | undefined, documentId: string): string {
  const doc = (documentId || "").toUpperCase();
  const m = meta || {};
  if (m.document_type) return String(m.document_type).toUpperCase();
  if (m.classification) return String(m.classification).toUpperCase();
  if (doc.includes("SOP")) return "SOP";
  if (doc.includes("DRG") || doc.includes("DS")) return "Asset";
  if (doc.includes("MNT") || doc.includes("PM")) return "Maintenance";
  if (doc.includes("INS") || doc.includes("REP")) return "Inspection";
  if (doc.includes("POL")) return "Policy";
  if (doc.includes("VEN")) return "Vendor";
  return "Document";
}

export default function KnowledgeScreen() {
  const [query, setQuery] = useState("What is the maximum operating pressure for P-102?");
  const [activeFilter, setActiveFilter] = useState("All");
  const [results, setResults] = useState<KnowledgeSearchResult[]>([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runSearch = useCallback(async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      const data = await api.knowledge.search({ query: q.trim(), limit: 20 });
      setResults(data.results || []);
    } catch (e) {
      setResults([]);
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void runSearch(query);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const filtered = activeFilter === "All"
    ? results
    : results.filter((r) => inferType(r.metadata, r.document_id) === activeFilter);

  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      <div className="max-w-4xl mx-auto px-6 py-6">
        <div className="mb-6">
          <h1 className="text-[22px] font-semibold text-[#F5F7FA] mb-1">Company Knowledge</h1>
          <p className="text-[12px] text-[#667386]">Search ApexPetro's documents, SOPs, inspection records, and data. All retrieval is local.</p>
        </div>

        <div className="rounded-xl bg-[#0F1726] border border-[#8B5CF6]/30 focus-within:border-[#8B5CF6]/50 transition-all mb-4 overflow-hidden">
          <div className="flex items-center gap-3 px-4 py-3">
            <Search size={15} className="text-[#8B5CF6] flex-none" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") void runSearch(query); }}
              placeholder="Search your organization's knowledge..."
              className="flex-1 bg-transparent text-[14px] text-[#F5F7FA] placeholder-[#667386] outline-none"
            />
            <button
              onClick={() => void runSearch(query)}
              disabled={loading}
              className="h-7 px-3.5 bg-[#8B5CF6] hover:bg-[#7C3AED] disabled:opacity-60 text-white text-[12px] font-semibold rounded-lg transition-colors flex items-center gap-1.5"
            >
              {loading && <Loader2 size={11} className="animate-spin" />} Search
            </button>
          </div>
        </div>

        <div className="flex items-center gap-1.5 flex-wrap mb-5">
          <Filter size={12} className="text-[#667386]" />
          {filterTags.map((tag) => (
            <button
              key={tag}
              onClick={() => setActiveFilter(tag)}
              className={`h-6 px-2.5 rounded-md text-[11px] font-medium transition-all ${
                activeFilter === tag
                  ? "bg-[#8B5CF6]/15 text-[#8B5CF6] border border-[#8B5CF6]/30"
                  : "text-[#667386] hover:text-[#9AA6B5] bg-[#141E2F] border border-[#253248]"
              }`}
            >
              {tag}
            </button>
          ))}
        </div>

        {searched && (
          <>
            <div className="flex items-center gap-2 mb-3">
              <p className="text-[11px] text-[#667386]">
                {loading ? "Searching…" : `${filtered.length} results for `}
                {!loading && <span className="text-[#F5F7FA] font-medium">"{query}"</span>}
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
                {[0, 1, 2].map((i) => (
                  <div key={i} className="rounded-xl bg-[#0F1726] border border-[#253248] p-5 animate-pulse">
                    <div className="h-3 w-1/3 bg-[#253248] rounded mb-2" />
                    <div className="h-2.5 w-full bg-[#1a2740] rounded mb-1.5" />
                    <div className="h-2.5 w-2/3 bg-[#1a2740] rounded" />
                  </div>
                ))}
              </div>
            ) : filtered.length === 0 ? (
              <div className="rounded-xl bg-[#0F1726] border border-[#253248] px-5 py-10 text-center">
                <BookOpen size={20} className="text-[#667386] mx-auto mb-2" />
                <p className="text-[13px] text-[#9AA6B5]">No knowledge base results found for this query.</p>
                <p className="text-[11px] text-[#667386] mt-1">Try rephrasing or removing filters.</p>
              </div>
            ) : (
              <div className="space-y-2.5">
                {filtered.map((result) => {
                  const type = inferType(result.metadata, result.document_id);
                  const classification = result.metadata?.classification || "INTERNAL";
                  const relevance = Math.round((result.score ?? 0) * 100);
                  return (
                    <div key={result.chunk_id} className="rounded-xl bg-[#0F1726] border border-[#253248] hover:border-[#2e3e57] transition-all cursor-pointer group">
                      <div className="px-5 py-4">
                        <div className="flex items-start justify-between gap-3 mb-2">
                          <div className="flex items-center gap-2 flex-wrap">
                            <h3 className="text-[13px] font-semibold text-[#F5F7FA] group-hover:text-white transition-colors break-all">
                              {result.document_id}
                            </h3>
                            <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded ${typeColors[type] || "text-[#9AA6B5] bg-[#253248]"}`}>
                              {type}
                            </span>
                            <span className="text-[9px] font-semibold text-[#F59E0B] bg-[#F59E0B]/8 px-1.5 py-0.5 rounded">
                              {classification}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 flex-none">
                            <div className="w-8 h-1 bg-[#253248] rounded-full overflow-hidden">
                              <div className="h-full bg-[#8B5CF6] rounded-full" style={{ width: `${Math.min(100, relevance)}%` }} />
                            </div>
                            <span className="text-[10px] font-mono text-[#667386]">{relevance}%</span>
                          </div>
                        </div>
                        <p className="text-[11px] text-[#8B5CF6] mb-1.5">
                          {result.section || (result.page_number ? `Page ${result.page_number}` : "Extracted passage")}
                        </p>
                        <p className="text-[12px] text-[#9AA6B5] leading-relaxed line-clamp-2">{result.content}</p>
                        <div className="flex items-center gap-3 mt-2">
                          <FileText size={11} className="text-[#3a4a60]" />
                          <span className="text-[10px] text-[#667386]">
                            Chunk {result.chunk_id}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
