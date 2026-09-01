import { useState, useEffect } from "react";
import { api, Project } from "../services/api";
import { FolderOpen, Clock, FileText, Package, AlertTriangle, ChevronRight, Plus, Loader } from "lucide-react";

export default function ProjectsScreen({ onSelectProject }: { onSelectProject?: () => void }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState({ totalProjects: 0, totalDocuments: 0, totalAssets: 0, totalTasks: 0 });

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      api.projects.list(),
      api.documents.list(),
      api.assets.list(),
      api.tasks.list(),
    ]).then(([projectsRes, docsRes, assetsRes, tasksRes]) => {
      setProjects(projectsRes.projects);
      setStats({
        totalProjects: projectsRes.total,
        totalDocuments: docsRes.total,
        totalAssets: assetsRes.total,
        totalTasks: tasksRes.total,
      });
      setLoading(false);
    }).catch(e => {
      setError(e.message);
      setLoading(false);
    });
  }, []);

  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      <div className="max-w-4xl mx-auto px-6 py-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-[22px] font-semibold text-[#F5F7FA]">Projects</h1>
            <p className="text-[12px] text-[#667386] mt-0.5">ApexPetro Energy Limited · Jamnagar Refinery</p>
          </div>
          <button className="flex items-center gap-2 h-8 px-3.5 rounded-lg bg-[#8B5CF6] hover:bg-[#7C3AED] text-white text-[12px] font-semibold transition-colors">
            <Plus size={13} />
            New Project
          </button>
        </div>

        <div className="grid grid-cols-4 gap-3 mb-6">
          {[
            { label: "Projects", value: String(stats.totalProjects), color: "text-[#F5F7FA]" },
            { label: "Documents", value: String(stats.totalDocuments), color: "text-[#3B82F6]" },
            { label: "Assets", value: String(stats.totalAssets), color: "text-[#22C55E]" },
            { label: "Tasks", value: String(stats.totalTasks), color: "text-[#8B5CF6]" },
          ].map(({ label, value, color }) => (
            <div key={label} className="rounded-lg bg-[#0F1726] border border-[#253248] px-4 py-3">
              <p className={`text-[22px] font-semibold ${color}`}>{value}</p>
              <p className="text-[11px] text-[#667386]">{label}</p>
            </div>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader size={24} className="text-[#8B5CF6] animate-spin" />
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <p className="text-[13px] text-[#EF4444]">{error}</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-20">
            <FolderOpen size={32} className="text-[#253248] mx-auto mb-3" />
            <p className="text-[13px] text-[#667386]">No projects yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {projects.map((project: Project) => {
              const p = {
                id: project.project_id,
                name: project.name,
                unit: project.unit,
                asset: project.asset,
                status: project.status,
                statusColor: project.status === 'Completed' ? 'text-[#22C55E]' : 'text-[#3B82F6]',
                statusBg: 'bg-[#3B82F6]/10 border-[#3B82F6]/25',
                risk: project.risk,
                riskColor: project.risk === 'HIGH' ? 'text-[#EF4444]' : 'text-[#F59E0B]',
                progress: project.progress,
                lastActivity: new Date(project.updated_at).toLocaleString(),
                classification: project.classification,
              };
              return (
                <div
                  key={p.id}
                  onClick={onSelectProject}
                  className="rounded-xl bg-[#0F1726] border border-[#253248] hover:border-[#2e3e57] transition-all cursor-pointer group overflow-hidden"
                >
                  <div className="px-5 py-4">
                    <div className="flex items-start gap-4">
                      <div className="w-9 h-9 rounded-lg bg-[#141E2F] border border-[#253248] flex items-center justify-center flex-none">
                        <FolderOpen size={16} className="text-[#8B5CF6]" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <h3 className="text-[14px] font-semibold text-[#F5F7FA] group-hover:text-white transition-colors">
                              {p.name}
                            </h3>
                            <div className="flex items-center gap-2 mt-0.5">
                              <p className="text-[11px] text-[#667386]">{p.unit}</p>
                              {p.asset !== "—" && (
                                <>
                                  <span className="text-[#253248]">·</span>
                                  <p className="text-[11px] text-[#667386]">{p.asset}</p>
                                </>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2 flex-none">
                            {p.risk !== "—" && (
                              <span className={`text-[10px] font-bold ${p.riskColor}`}>{p.risk}</span>
                            )}
                            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md border ${p.statusBg} ${p.statusColor}`}>
                              {p.status}
                            </span>
                            <span className="text-[9px] font-semibold text-[#F59E0B] bg-[#F59E0B]/8 px-1.5 py-0.5 rounded">
                              {p.classification}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 mt-3">
                          <div className="flex items-center gap-2 flex-1">
                            <div className="flex-1 h-1 bg-[#253248] rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full bg-gradient-to-r from-[#8B5CF6] to-[#14B8A6]"
                                style={{ width: `${p.progress}%` }}
                              />
                            </div>
                            <span className="text-[10px] font-mono text-[#667386] flex-none">{p.progress}%</span>
                          </div>

                          <div className="flex items-center gap-3 flex-none">
                            <div className="flex items-center gap-1 text-[#667386]">
                              <Clock size={10} />
                              <span className="text-[10px]">{p.lastActivity}</span>
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
