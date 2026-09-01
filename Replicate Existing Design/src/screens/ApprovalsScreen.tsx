import { useState, useEffect } from "react";
import { AlertTriangle, Check, X } from "lucide-react";
import { api, Approval } from "../services/api";

const riskFor = (status: string) => {
  const s = (status || "").toLowerCase();
  if (s.includes("approv")) return { risk: "LOW", riskColor: "text-[#22C55E]", riskBg: "bg-[#22C55E]/10 border-[#22C55E]/20" };
  if (s.includes("reject")) return { risk: "HIGH", riskColor: "text-[#EF4444]", riskBg: "bg-[#EF4444]/10 border-[#EF4444]/20" };
  return { risk: "MEDIUM", riskColor: "text-[#F59E0B]", riskBg: "bg-[#F59E0B]/10 border-[#F59E0B]/20" };
};

function StatusBadge({ status }: { status: string }) {
  const s = (status || "").toLowerCase();
  if (s.includes("approv")) return <Check size={14} className="text-[#22C55E]" />;
  if (s.includes("reject") || s.includes("den")) return <X size={14} className="text-[#EF4444]" />;
  return <AlertTriangle size={14} className="text-[#F59E0B]" />;
}

function ApprovalCard({ approval }: { approval: Approval }) {
  const pending = !(approval.status || "").toLowerCase().includes("approv") && !(approval.status || "").toLowerCase().includes("reject");
  const { risk, riskColor, riskBg } = riskFor(approval.status);
  const requestedAt = new Date(approval.requested_at).toLocaleString();

  return (
    <div className={`rounded-xl border overflow-hidden transition-all ${pending ? "bg-[#0F1726] border-[#F59E0B]/30" : "bg-[#0F1726] border-[#253248]"}`}>
      <div className={`px-5 py-3 border-b flex items-center gap-3 ${pending ? "border-[#F59E0B]/20 bg-[#F59E0B]/4" : "border-[#253248]"}`}>
        <StatusBadge status={approval.status} />
        <p className={`text-[12px] font-semibold ${pending ? "text-[#F59E0B]" : "text-[#22C55E]"}`}>
          {pending ? "Human Review Required" : approval.status}
        </p>
        <span className="ml-auto text-[10px] text-[#667386]">{requestedAt}</span>
      </div>

      <div className="px-5 py-4">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <h3 className="text-[15px] font-semibold text-[#F5F7FA]">Approval {approval.approval_id}</h3>
            <p className="text-[11px] text-[#667386] mt-0.5">Status: {approval.status}</p>
          </div>
          <span className={`flex items-center gap-1.5 text-[11px] font-bold px-2.5 py-1 rounded-lg border ${riskBg} ${riskColor}`}>
            {risk} RISK
          </span>
        </div>

        <div className="grid grid-cols-4 gap-3 mb-4">
          {[
            { label: "Risk", value: risk, color: riskColor },
            { label: "Requested", value: new Date(approval.requested_at).toLocaleDateString(), color: "text-[#9AA6B5]" },
            { label: "Reviewed", value: approval.reviewed_at ? new Date(approval.reviewed_at).toLocaleDateString() : "—", color: "text-[#9AA6B5]" },
            { label: "Approval ID", value: approval.approval_id, color: "text-[#9AA6B5]" },
          ].map(({ label, value, color }) => (
            <div key={label} className="rounded-lg bg-[#141E2F] border border-[#253248] p-2.5">
              <p className="text-[9px] text-[#667386] mb-1">{label}</p>
              <p className={`text-[11px] font-semibold ${color}`}>{value}</p>
            </div>
          ))}
        </div>

        <div className={`rounded-lg p-3.5 mb-4 ${pending ? "bg-[#F59E0B]/6 border border-[#F59E0B]/20" : "bg-[#141E2F] border border-[#253248]"}`}>
          <p className="text-[10px] text-[#667386] mb-1 font-semibold uppercase tracking-wide">Comments</p>
          <p className="text-[13px] text-[#F5F7FA] italic leading-relaxed">{approval.comments || "No comments provided."}</p>
          <p className="text-[10px] text-[#667386] mt-2">AI-generated · Requires authorized human review</p>
        </div>
      </div>
    </div>
  );
}

export default function ApprovalsScreen() {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.approvals.list();
        if (!active) return;
        setApprovals(data.approvals || []);
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "Failed to load approvals");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  const pending = approvals.filter(a => !(a.status || "").toLowerCase().includes("approv") && !(a.status || "").toLowerCase().includes("reject"));
  const completed = approvals.filter(a => (a.status || "").toLowerCase().includes("approv") || (a.status || "").toLowerCase().includes("reject"));

  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      <div className="max-w-3xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-[22px] font-semibold text-[#F5F7FA]">Approvals</h1>
            <p className="text-[12px] text-[#667386] mt-0.5">AI-generated recommendations requiring human decision</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold text-[#F59E0B] bg-[#F59E0B]/10 border border-[#F59E0B]/25 px-2.5 py-1 rounded-full">
              {pending.length} pending
            </span>
          </div>
        </div>

        {error && (
          <div className="rounded-xl bg-[#7F1D1D]/15 border border-[#7F1D1D]/40 px-4 py-3 flex items-start gap-2.5 mb-4">
            <AlertTriangle size={14} className="text-[#FCA5A5] flex-none mt-0.5" />
            <p className="text-[12.5px] text-[#FCA5A5]">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="space-y-4">
            {[0, 1].map((i) => (
              <div key={i} className="rounded-xl bg-[#0F1726] border border-[#253248] p-5 animate-pulse">
                <div className="h-3 w-1/3 bg-[#253248] rounded mb-2" />
                <div className="h-2.5 w-2/3 bg-[#1a2740] rounded" />
              </div>
            ))}
          </div>
        ) : approvals.length === 0 ? (
          <div className="text-center py-16">
            <Check size={32} className="text-[#253248] mx-auto mb-3" />
            <p className="text-[14px] text-[#667386]">No approvals yet.</p>
            <p className="text-[12px] text-[#667386] mt-1">AI-generated recommendations will appear here for your review.</p>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              {pending.map((ap) => (
                <ApprovalCard key={ap.id} approval={ap} />
              ))}
            </div>

            {completed.length > 0 && (
              <div className="mt-8">
                <p className="text-[11px] font-semibold text-[#667386] uppercase tracking-widest mb-3">Completed</p>
                <div className="space-y-3">
                  {completed.map((ap) => (
                    <ApprovalCard key={ap.id} approval={ap} />
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
