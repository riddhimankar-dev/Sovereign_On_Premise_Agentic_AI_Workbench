import { ChevronLeft, ShieldCheck, Key, Bell, Cpu, HardDrive, Clock, LogOut, ChevronRight } from "lucide-react";

interface ProfileScreenProps { onBack: () => void; }

export default function ProfileScreen({ onBack }: ProfileScreenProps) {
  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      <div className="max-w-2xl mx-auto px-6 py-6">
        {/* Back nav */}
        <button onClick={onBack} className="flex items-center gap-1.5 text-[11px] text-[#667386] hover:text-[#9AA6B5] transition-colors mb-6">
          <ChevronLeft size={13}/> Back
        </button>

        {/* Profile card */}
        <div className="rounded-[8px] bg-[#0F1726] border border-[#253248] px-6 py-6 mb-4 flex items-center gap-5">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-[#8B5CF6] to-[#6D28D9] flex items-center justify-center text-white text-[22px] font-semibold shadow-xl shadow-[#8B5CF6]/20 flex-none">
            AM
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-[20px] font-semibold text-[#F5F7FA]">Arjun Mehta</h1>
            <p className="text-[13px] text-[#9AA6B5] mt-0.5">Inspection Engineer</p>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-[10px] font-semibold text-[#14B8A6] bg-[#14B8A6]/10 border border-[#14B8A6]/20 px-2 py-0.5 rounded-[4px]">ACTIVE</span>
              <span className="text-[10.5px] text-[#667386]">arjun.mehta@apexpetro.com</span>
            </div>
          </div>
          <button className="h-8 px-4 rounded-[6px] border border-[#253248] text-[11.5px] text-[#9AA6B5] hover:bg-[#141E2F] hover:text-[#F5F7FA] transition-all">
            Edit Profile
          </button>
        </div>

        {/* Organization */}
        <div className="rounded-[8px] bg-[#0F1726] border border-[#253248] px-5 py-4 mb-4">
          <p className="text-[9px] font-semibold tracking-[0.14em] text-[#3a4a60] uppercase mb-3">Organization</p>
          <div className="grid grid-cols-2 gap-3">
            {[
              { k: "Company",        v: "ApexPetro Energy Limited" },
              { k: "Site",           v: "Jamnagar Refinery" },
              { k: "Department",     v: "Integrity & Inspection" },
              { k: "Employee ID",    v: "APX-INS-0142" },
              { k: "Clearance",      v: "CONFIDENTIAL", warn: true },
              { k: "Environment",    v: "Local — Sovereign AI Workbench" },
            ].map(({ k, v, warn }) => (
              <div key={k}>
                <p className="text-[10px] text-[#667386]">{k}</p>
                <p className={`text-[12px] font-medium mt-0.5 ${warn ? "text-[#F59E0B]" : "text-[#F5F7FA]"}`}>{v}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Permissions */}
        <div className="rounded-[8px] bg-[#0F1726] border border-[#253248] px-5 py-4 mb-4">
          <p className="text-[9px] font-semibold tracking-[0.14em] text-[#3a4a60] uppercase mb-3">Access & Permissions</p>
          <div className="space-y-2">
            {[
              { label: "View CONFIDENTIAL documents",        granted: true },
              { label: "Run AI analysis on inspection data", granted: true },
              { label: "Execute secure code sandbox",        granted: true },
              { label: "Submit approvals",                   granted: false },
              { label: "Manage knowledge base",              granted: false },
              { label: "Configure system models",            granted: false },
            ].map(({ label, granted }) => (
              <div key={label} className="flex items-center justify-between py-1.5 border-b border-[#1a2740] last:border-0">
                <p className="text-[12px] text-[#9AA6B5]">{label}</p>
                {granted ? (
                  <span className="text-[9.5px] font-semibold text-[#22C55E] bg-[#22C55E]/10 px-2 py-0.5 rounded-[4px]">Granted</span>
                ) : (
                  <span className="text-[9.5px] font-semibold text-[#667386] bg-[#253248] px-2 py-0.5 rounded-[4px]">Restricted</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Preferences */}
        <div className="rounded-[8px] bg-[#0F1726] border border-[#253248] overflow-hidden mb-4">
          <p className="text-[9px] font-semibold tracking-[0.14em] text-[#3a4a60] uppercase px-5 pt-4 pb-3">Preferences</p>
          {[
            { icon: Bell,        label: "Notifications",       desc: "Approvals, task completions, alerts"  },
            { icon: Key,         label: "API Keys",             desc: "Manage local integration keys"        },
            { icon: ShieldCheck, label: "Security settings",    desc: "2FA, session timeout, audit log"      },
          ].map(({ icon: Icon, label, desc }) => (
            <button key={label} className="w-full flex items-center gap-3 px-5 py-3.5 hover:bg-[#141E2F] border-t border-[#1a2740] first:border-0 transition-colors group">
              <div className="w-8 h-8 rounded-[6px] bg-[#141E2F] group-hover:bg-[#182337] flex items-center justify-center flex-none transition-colors">
                <Icon size={14} className="text-[#667386] group-hover:text-[#9AA6B5] transition-colors"/>
              </div>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-[12.5px] font-medium text-[#F5F7FA]">{label}</p>
                <p className="text-[10.5px] text-[#667386]">{desc}</p>
              </div>
              <ChevronRight size={12} className="text-[#3a4a60] group-hover:text-[#667386] flex-none transition-colors"/>
            </button>
          ))}
        </div>

        {/* Local environment stats */}
        <div className="rounded-[8px] bg-[#0F1726] border border-[#253248] px-5 py-4 mb-4">
          <p className="text-[9px] font-semibold tracking-[0.14em] text-[#3a4a60] uppercase mb-3">Local Environment</p>
          <div className="grid grid-cols-3 gap-2.5">
            {[
              { icon: Cpu,      label: "GPU",     value: "NVIDIA RTX A5000", sub: "18.4/24 GB", color: "text-[#8B5CF6]" },
              { icon: HardDrive, label: "Storage", value: "Local NVMe",       sub: "2.4 TB free", color: "text-[#14B8A6]" },
              { icon: Clock,     label: "Uptime",  value: "4d 12h",           sub: "Since 2026-08-27", color: "text-[#9AA6B5]" },
            ].map(({ icon: Icon, label, value, sub, color }) => (
              <div key={label} className="rounded-[6px] bg-[#141E2F] border border-[#253248] p-3">
                <Icon size={13} className={`${color} mb-2`}/>
                <p className="text-[9px] text-[#667386] uppercase tracking-wide">{label}</p>
                <p className="text-[12px] font-medium text-[#F5F7FA] mt-0.5">{value}</p>
                <p className="text-[10px] text-[#667386] mt-0.5">{sub}</p>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-[#1a2740]">
            <span className="w-[5px] h-[5px] rounded-full bg-[#14B8A6] animate-pulse-dot"/>
            <p className="text-[10.5px] text-[#14B8A6]">All processing is local. No data transmitted externally.</p>
          </div>
        </div>

        {/* Sign out */}
        <button className="w-full flex items-center justify-center gap-2 h-10 rounded-[6px] border border-[#EF4444]/25 text-[#EF4444] text-[12.5px] font-medium hover:bg-[#EF4444]/8 transition-all">
          <LogOut size={14}/> Sign Out
        </button>
      </div>
    </div>
  );
}
