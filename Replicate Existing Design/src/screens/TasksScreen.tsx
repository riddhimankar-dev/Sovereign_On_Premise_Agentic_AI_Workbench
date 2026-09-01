import { useState, useEffect } from "react";
import { CheckSquare, Clock, Zap, AlertTriangle, Loader2, Check, ChevronRight } from "lucide-react";
import { api, Task } from "../services/api";

const statusColors: Record<string, { color: string; bg: string }> = {
  completed: { color: "text-[#22C55E]", bg: "bg-[#22C55E]/10 border-[#22C55E]/25" },
  approved: { color: "text-[#22C55E]", bg: "bg-[#22C55E]/10 border-[#22C55E]/25" },
  running: { color: "text-[#3B82F6]", bg: "bg-[#3B82F6]/10 border-[#3B82F6]/25" },
  in_progress: { color: "text-[#3B82F6]", bg: "bg-[#3B82F6]/10 border-[#3B82F6]/25" },
  pending: { color: "text-[#F59E0B]", bg: "bg-[#F59E0B]/10 border-[#F59E0B]/25" },
  awaiting: { color: "text-[#F59E0B]", bg: "bg-[#F59E0B]/10 border-[#F59E0B]/25" },
};

function statusStyle(status: string) {
  const s = (status || "pending").toLowerCase();
  return statusColors[s] || statusColors.pending;
}

function statusIcon(status: string) {
  const s = (status || "").toLowerCase();
  if (s.includes("complete") || s.includes("approv") || s.includes("done")) return Check;
  if (s.includes("runn") || s.includes("in_prog") || s.includes("process")) return Loader2;
  return AlertTriangle;
}

function formatDate(dueDate: string | null) {
  if (!dueDate) return "No deadline";
  return new Date(dueDate).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export default function TasksScreen() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.tasks.list();
        if (!active) return;
        setTasks(data.tasks || []);
      } catch (e) {
        if (active) setError(e instanceof Error ? e.message : "Failed to load tasks");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, []);

  const filtered = filter === "All" ? tasks : tasks.filter(t => (t.status || "").toLowerCase().includes(filter.toLowerCase()));

  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      <div className="max-w-4xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-[22px] font-semibold text-[#F5F7FA]">My Tasks</h1>
            <p className="text-[12px] text-[#667386] mt-0.5">Arjun Mehta · Inspection & Integrity</p>
          </div>
          <div className="flex items-center gap-2">
            {["All", "Running", "Awaiting", "Completed"].map((f) => (
              <button key={f} onClick={() => setFilter(f)} className={`h-7 px-3 rounded-md text-[11px] transition-all ${filter === f ? "bg-[#8B5CF6]/15 text-[#8B5CF6] border border-[#8B5CF6]/30" : "text-[#667386] hover:text-[#9AA6B5] hover:bg-[#141E2F]"}`}>
                {f}
              </button>
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
        ) : filtered.length === 0 ? (
          <div className="text-center py-16">
            <CheckSquare size={32} className="text-[#253248] mx-auto mb-3" />
            <p className="text-[14px] text-[#667386]">No tasks here yet.</p>
            <p className="text-[12px] text-[#667386] mt-1">Assigned AI work items will appear here.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((task) => {
              const StatusIcon = statusIcon(task.status);
              const style = statusStyle(task.status);
              return (
                <div key={task.id} className="rounded-xl bg-[#0F1726] border border-[#253248] hover:border-[#2e3e57] cursor-pointer transition-all group">
                  <div className="px-5 py-4">
                    <div className="flex items-start gap-4">
                      <div className="w-9 h-9 rounded-lg bg-[#141E2F] border border-[#253248] flex items-center justify-center flex-none">
                        <CheckSquare size={15} className="text-[#8B5CF6]" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-3 mb-2">
                          <div>
                            <h3 className="text-[14px] font-semibold text-[#F5F7FA]">{task.title}</h3>
                            <p className="text-[11px] text-[#667386] mt-0.5">Task {task.task_id}</p>
                          </div>
                          <div className="flex items-center gap-2 flex-none">
                            <span className={`flex items-center gap-1.5 text-[10px] font-semibold px-2 py-0.5 rounded-md border ${style.bg} ${style.color}`}>
                              <StatusIcon size={10} className={(task.status || "").toLowerCase().includes("runn") ? "animate-spin" : ""} />
                              {task.status}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-4">
                          <div className="flex items-center gap-1 flex-1">
                            <Zap size={10} className="text-[#8B5CF6]" />
                            <span className="text-[10px] text-[#667386]">Priority {task.priority}</span>
                          </div>
                          <div className="flex items-center gap-3 flex-none">
                            <div className="flex items-center gap-1">
                              <CheckSquare size={10} className="text-[#667386]" />
                              <span className="text-[10px] text-[#667386]">{task.asset || "No asset"}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Clock size={10} className="text-[#667386]" />
                              <span className="text-[10px] text-[#667386]">{formatDate(task.due_date)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <ChevronRight size={14} className="text-[#253248] group-hover:text-[#667386] transition-colors flex-none mt-1" />
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
