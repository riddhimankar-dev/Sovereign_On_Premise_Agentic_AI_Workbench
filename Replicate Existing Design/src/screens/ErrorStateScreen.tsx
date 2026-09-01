import { AlertTriangle, RefreshCw, Cpu, FileText, Terminal, Shield, WifiOff, Clock } from "lucide-react";

interface ErrorStateScreenProps { onBack?: () => void; }

function ErrorCard({
  icon: Icon,
  iconColor,
  iconBg,
  title,
  subtitle,
  message,
  detail,
  actions,
  extraContent,
}: {
  icon: React.ElementType;
  iconColor: string;
  iconBg: string;
  title: string;
  subtitle: string;
  message: string;
  detail?: string;
  actions: { label: string; primary?: boolean; danger?: boolean }[];
  extraContent?: React.ReactNode;
}) {
  return (
    <div className="rounded-[8px] bg-[#0F1726] border border-[#253248] overflow-hidden">
      <div className="px-5 py-4 border-b border-[#1a2740] flex items-center gap-3">
        <div className={`w-8 h-8 rounded-[6px] ${iconBg} flex items-center justify-center flex-none`}>
          <Icon size={15} className={iconColor}/>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[13px] font-semibold text-[#F5F7FA]">{title}</p>
          <p className="text-[10.5px] text-[#667386] mt-0.5">{subtitle}</p>
        </div>
        <div className="flex items-center gap-1.5 flex-none">
          <span className="w-1.5 h-1.5 rounded-full bg-[#EF4444]"/>
          <span className="text-[9.5px] font-semibold text-[#EF4444] tracking-wide">ERROR</span>
        </div>
      </div>
      <div className="px-5 py-4">
        <div className="rounded-[6px] bg-[#EF4444]/6 border border-[#EF4444]/20 px-4 py-3 mb-4">
          <div className="flex items-start gap-2.5">
            <AlertTriangle size={13} className="text-[#EF4444] flex-none mt-0.5"/>
            <div>
              <p className="text-[13px] font-semibold text-[#EF4444] mb-0.5">{message}</p>
              {detail && <p className="text-[11.5px] text-[#9AA6B5] leading-relaxed">{detail}</p>}
            </div>
          </div>
        </div>
        {extraContent}
        <div className="flex gap-2">
          {actions.map(({ label, primary, danger }) => (
            <button key={label} className={`h-8 px-4 rounded-[6px] text-[11.5px] font-semibold transition-all flex items-center gap-1.5 ${
              primary ? "bg-[#8B5CF6] hover:bg-[#7C3AED] text-white"
              : danger ? "border border-[#EF4444]/30 text-[#EF4444] hover:bg-[#EF4444]/10"
              : "border border-[#253248] text-[#9AA6B5] hover:bg-[#141E2F] hover:text-[#F5F7FA]"
            }`}>
              {label === "Retry" && <RefreshCw size={11}/>} {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ErrorStateScreen({ onBack }: ErrorStateScreenProps) {
  return (
    <div className="h-full overflow-y-auto bg-[#080D18]">
      <div className="max-w-2xl mx-auto px-6 py-6">
        <div className="mb-6">
          <h1 className="text-[22px] font-semibold text-[#F5F7FA] mb-1">Error States</h1>
          <p className="text-[12px] text-[#667386]">System error states — Screen 24</p>
        </div>

        <div className="space-y-4">
          {/* Error 1: Model unavailable */}
          <ErrorCard
            icon={Cpu}
            iconColor="text-[#EF4444]"
            iconBg="bg-[#EF4444]/12"
            title="Local model unavailable"
            subtitle="AI Model · Qwen 2.5 32B Instruct"
            message="Local model unavailable"
            detail="The selected model is currently unavailable. The GPU process may have terminated or run out of memory. No data was lost."
            actions={[
              { label: "Retry", primary: true },
              { label: "Switch Model" },
              { label: "View Details" },
            ]}
            extraContent={
              <div className="rounded-[6px] bg-[#141E2F] border border-[#253248] px-3.5 py-3 mb-4 space-y-1.5">
                {[
                  { k: "Model",        v: "Qwen 2.5 32B Instruct" },
                  { k: "Status",       v: "Unavailable",     c: "text-[#EF4444]" },
                  { k: "GPU Memory",   v: "24 / 24 GB",      c: "text-[#F59E0B]" },
                  { k: "Last seen",    v: "09:41:52" },
                ].map(({ k, v, c }) => (
                  <div key={k} className="flex items-center justify-between">
                    <p className="text-[10px] text-[#667386]">{k}</p>
                    <p className={`text-[10.5px] font-medium ${c || "text-[#9AA6B5]"}`}>{v}</p>
                  </div>
                ))}
              </div>
            }
          />

          {/* Error 2: Document processing failed */}
          <ErrorCard
            icon={FileText}
            iconColor="text-[#EF4444]"
            iconBg="bg-[#EF4444]/12"
            title="Unable to process document"
            subtitle="Files · P-102_Maintenance_History.xlsx"
            message="Document processing failed"
            detail="The system was unable to extract content from this file. The file may be corrupted, password-protected, or in an unsupported format."
            actions={[
              { label: "Retry", primary: true },
              { label: "View details" },
            ]}
            extraContent={
              <div className="rounded-[6px] bg-[#141E2F] border border-[#253248] px-3.5 py-3 mb-4">
                <div className="space-y-2">
                  {[
                    { label: "File received",           done: true },
                    { label: "Security classification", done: true },
                    { label: "OCR",                     done: false, err: true },
                  ].map(({ label, done, err }) => (
                    <div key={label} className="flex items-center gap-2.5">
                      <div className={`w-[14px] h-[14px] rounded-full flex items-center justify-center flex-none ${
                        err ? "bg-[#EF4444]/15" : done ? "bg-[#14B8A6]/15" : "border border-[#253248]"
                      }`}>
                        {err
                          ? <AlertTriangle size={8} className="text-[#EF4444]"/>
                          : done
                          ? <span className="text-[8px] text-[#14B8A6]">✓</span>
                          : null}
                      </div>
                      <p className={`text-[11px] ${err ? "text-[#EF4444]" : done ? "text-[#9AA6B5]" : "text-[#3a4a60]"}`}>{label}</p>
                    </div>
                  ))}
                </div>
                <p className="text-[10px] text-[#EF4444] mt-3 pt-3 border-t border-[#253248]">
                  Error: Failed to parse Excel file. File may be corrupted or encrypted.
                </p>
              </div>
            }
          />

          {/* Error 3: Sandbox execution failed */}
          <ErrorCard
            icon={Terminal}
            iconColor="text-[#EF4444]"
            iconBg="bg-[#EF4444]/12"
            title="Execution failed"
            subtitle="Secure Code Sandbox · main.py"
            message="Execution failed"
            detail="The sandbox encountered an error during execution. The container has been destroyed and no data was retained."
            actions={[
              { label: "Retry", primary: true },
              { label: "Clear Output" },
            ]}
            extraContent={
              <div className="rounded-[6px] bg-[#080D18] border border-[#EF4444]/20 px-4 py-3 mb-4 font-mono text-[12px]">
                <p className="text-[8.5px] font-semibold tracking-[0.14em] text-[#667386] uppercase mb-2 font-sans">Execution Output</p>
                <p className="text-[#EF4444]">Traceback (most recent call last):</p>
                <p className="text-[#9AA6B5] pl-2">File "main.py", line 4, in &lt;module&gt;</p>
                <p className="text-[#EF4444] pl-4">ZeroDivisionError: division by zero</p>
                <p className="text-[#667386] border-t border-[#253248] mt-2 pt-2 text-[11px] font-sans">Container destroyed · Execution time: 0.12s</p>
              </div>
            }
          />

          {/* Error 4: Connection / network blocked */}
          <div className="rounded-[8px] bg-[#0F1726] border border-[#253248] px-5 py-4 flex items-start gap-4">
            <div className="w-8 h-8 rounded-[6px] bg-[#141E2F] flex items-center justify-center flex-none">
              <WifiOff size={15} className="text-[#667386]"/>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-3 mb-1">
                <p className="text-[12.5px] font-semibold text-[#F5F7FA]">External network access blocked</p>
                <span className="text-[9.5px] font-semibold text-[#14B8A6] bg-[#14B8A6]/10 px-2 py-0.5 rounded-[4px]">BY DESIGN</span>
              </div>
              <p className="text-[11.5px] text-[#9AA6B5] leading-relaxed">
                The request attempted to reach an external endpoint. This is blocked by your organization's security policy. All work remains within ApexPetro's controlled environment.
              </p>
            </div>
          </div>

          {/* Error 5: Session timeout */}
          <div className="rounded-[8px] bg-[#0F1726] border border-[#253248] px-5 py-4 flex items-start gap-4">
            <div className="w-8 h-8 rounded-[6px] bg-[#F59E0B]/12 flex items-center justify-center flex-none">
              <Clock size={15} className="text-[#F59E0B]"/>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-3 mb-1">
                <p className="text-[12.5px] font-semibold text-[#F5F7FA]">Session timeout warning</p>
                <span className="text-[9.5px] font-semibold text-[#F59E0B] bg-[#F59E0B]/10 border border-[#F59E0B]/20 px-2 py-0.5 rounded-[4px]">WARNING</span>
              </div>
              <p className="text-[11.5px] text-[#9AA6B5] leading-relaxed mb-3">
                Your session will expire in 5 minutes due to inactivity. Unsaved work will be preserved in your conversation history.
              </p>
              <div className="flex gap-2">
                <button className="h-7 px-4 rounded-[5px] bg-[#8B5CF6] text-[11px] font-semibold text-white hover:bg-[#7C3AED] transition-all">
                  Stay Signed In
                </button>
                <button className="h-7 px-4 rounded-[5px] border border-[#253248] text-[11px] text-[#9AA6B5] hover:bg-[#141E2F] transition-all">
                  Sign Out
                </button>
              </div>
            </div>
          </div>

          {/* Security note */}
          <div className="rounded-[6px] bg-[#141E2F] border border-[#253248] px-4 py-3 flex items-start gap-2.5">
            <Shield size={13} className="text-[#14B8A6] flex-none mt-0.5"/>
            <p className="text-[11px] text-[#667386] leading-relaxed">
              Error messages shown here are safe, human-readable descriptions. Internal stack traces or sensitive system information are never exposed to the user interface.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
