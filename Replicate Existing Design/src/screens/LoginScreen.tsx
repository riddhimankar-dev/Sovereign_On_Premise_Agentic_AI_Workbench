import { useState } from "react";
import { Eye, EyeOff, Lock, ArrowRight, Loader2 } from "lucide-react";
import { api } from "../services/api";

interface LoginScreenProps {
  onLogin: () => void;
}

export default function LoginScreen({ onLogin }: LoginScreenProps) {
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("arjun.mehta@apexpetro.com");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function completeAuth(res: { access_token: string; full_name: string; email: string; role: string }) {
    localStorage.setItem("sovereign_token", res.access_token);
    localStorage.setItem("sovereign_user", JSON.stringify({ full_name: res.full_name, email: res.email, role: res.role }));
    onLogin();
  }

  async function handleLogin() {
    if (!email || !password) {
      setError("Please enter your email and password.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await api.auth.login({ email, password });
      completeAuth(res);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Login failed";
      setError(msg.includes("401") ? "Invalid email or password." : "Unable to reach the secure backend. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSignup() {
    if (!email || !password || !fullName.trim()) {
      setError("Please complete your name, work email, and password.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await api.auth.signup({ email, password, full_name: fullName.trim() });
      completeAuth(res);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Sign up failed";
      if (msg.includes("409")) {
        setError("An account with this email already exists. Please sign in instead.");
      } else if (msg.includes("422")) {
        setError("Please check the details and try again.");
      } else {
        setError("Unable to reach the secure backend. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  const isSignup = mode === "signup";

  function swapMode() {
    const target = isSignup ? "signin" : "signup";
    setMode(target);
    setError(null);
    setPassword("");
  }

  return (
    <div className="h-full flex bg-[#080D18] overflow-hidden">
      {/* Left panel — branding */}
      <div className="hidden lg:flex w-[480px] flex-none flex-col bg-[#0F1726] border-r border-[#253248] px-12 py-16 relative overflow-hidden">
        {/* Subtle background grid */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: "linear-gradient(#8B5CF6 1px, transparent 1px), linear-gradient(90deg, #8B5CF6 1px, transparent 1px)",
          backgroundSize: "40px 40px"
        }} />

        {/* Logo */}
        <div className="flex items-center gap-3 mb-16 relative z-10">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#8B5CF6] to-[#6D28D9] flex items-center justify-center shadow-lg shadow-[#8B5CF6]/20">
            <svg width="18" height="18" viewBox="0 0 14 14" fill="none">
              <path d="M7 1L2 4v6l5 3 5-3V4L7 1z" stroke="white" strokeWidth="1.3" fill="none" strokeLinejoin="round" />
              <path d="M7 1v12M2 4l5 3 5-3" stroke="white" strokeWidth="1.3" strokeLinecap="round" />
            </svg>
          </div>
          <div>
            <p className="text-[13px] font-semibold tracking-wider text-[#F5F7FA]">SOVEREIGN AI</p>
            <p className="text-[10px] font-medium tracking-[0.2em] text-[#667386]">WORKBENCH</p>
          </div>
        </div>

        <div className="relative z-10 flex-1">
          <p className="text-[11px] font-semibold tracking-widest text-[#8B5CF6] uppercase mb-4">Private intelligence for confidential industrial work</p>
          <h1 className="text-[38px] font-semibold text-[#F5F7FA] leading-tight mb-6">
            Your organization's<br />AI workbench.
          </h1>
          <p className="text-[14px] text-[#9AA6B5] leading-relaxed mb-12">
            Analyze confidential documents, work with company knowledge, run calculations, and generate business artifacts — entirely within your controlled environment.
          </p>

          <div className="space-y-4">
            {[
              { label: "Local inference only", desc: "All AI runs on your organization's hardware" },
              { label: "Company-isolated data", desc: "No cross-tenant access, ever" },
              { label: "Audit-logged activity", desc: "Every action tracked for compliance" },
              { label: "Air-gapped deployment", desc: "No internet connection required" },
            ].map(({ label, desc }) => (
              <div key={label} className="flex items-start gap-3">
                <div className="w-5 h-5 rounded-full bg-[#14B8A6]/15 border border-[#14B8A6]/25 flex items-center justify-center flex-none mt-0.5">
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path d="M2 5l2 2 4-4" stroke="#14B8A6" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
                <div>
                  <p className="text-[12px] font-medium text-[#F5F7FA]">{label}</p>
                  <p className="text-[11px] text-[#667386]">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom security badge */}
        <div className="relative z-10 mt-8">
          <div className="inline-flex items-center gap-2 px-3 py-2 rounded-full bg-[#14B8A6]/8 border border-[#14B8A6]/20">
            <span className="w-1.5 h-1.5 rounded-full bg-[#14B8A6] animate-pulse-dot" />
            <span className="text-[11px] font-semibold text-[#14B8A6] tracking-wide">LOCAL ONLY · NETWORK ISOLATED</span>
          </div>
        </div>
      </div>

      {/* Right panel — login form */}
      <div className="flex-1 flex items-center justify-center px-8 py-16">
        <div className="w-full max-w-[380px]">
          {/* Mobile logo */}
          <div className="flex items-center gap-2.5 mb-10 lg:hidden">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#8B5CF6] to-[#6D28D9] flex items-center justify-center">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M7 1L2 4v6l5 3 5-3V4L7 1z" stroke="white" strokeWidth="1.3" fill="none" strokeLinejoin="round" />
                <path d="M7 1v12M2 4l5 3 5-3" stroke="white" strokeWidth="1.3" strokeLinecap="round" />
              </svg>
            </div>
            <p className="text-[13px] font-semibold text-[#F5F7FA] tracking-wider">SOVEREIGN AI WORKBENCH</p>
          </div>

          {/* Company context */}
          <div className="rounded-xl bg-[#0F1726] border border-[#253248] p-4 mb-8">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#F59E0B] to-[#D97706] flex items-center justify-center text-white text-[11px] font-bold flex-none">
                AP
              </div>
              <div>
                <p className="text-[12px] font-semibold text-[#F5F7FA]">ApexPetro Energy Limited</p>
                <p className="text-[10px] text-[#667386]">Jamnagar Refinery Complex</p>
              </div>
              <div className="ml-auto flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#14B8A6] animate-pulse-dot" />
                <span className="text-[10px] text-[#14B8A6] font-medium">Local</span>
              </div>
            </div>
          </div>

          <h2 className="text-[24px] font-semibold text-[#F5F7FA] mb-1">{isSignup ? "Create your account" : "Sign in"}</h2>
          <p className="text-[13px] text-[#9AA6B5] mb-8">
            {isSignup ? "Join your organization's secure AI workbench." : "Access your secure AI workbench."}
          </p>

          <div className="space-y-4 mb-6">
            {/* Full name (signup only) */}
            {isSignup && (
              <div>
                <label className="block text-[11px] font-medium text-[#9AA6B5] mb-1.5 tracking-wide">
                  Full Name
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Priya Sharma"
                  className="w-full h-11 bg-[#0F1726] border border-[#253248] rounded-lg px-3.5 text-[14px] text-[#F5F7FA] placeholder-[#667386] outline-none focus:border-[#8B5CF6]/50 transition-colors"
                />
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-[11px] font-medium text-[#9AA6B5] mb-1.5 tracking-wide">
                Work Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-11 bg-[#0F1726] border border-[#253248] rounded-lg px-3.5 text-[14px] text-[#F5F7FA] placeholder-[#667386] outline-none focus:border-[#8B5CF6]/50 transition-colors"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-[11px] font-medium text-[#9AA6B5] mb-1.5 tracking-wide">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-11 bg-[#0F1726] border border-[#253248] rounded-lg px-3.5 pr-10 text-[14px] text-[#F5F7FA] placeholder-[#667386] outline-none focus:border-[#8B5CF6]/50 transition-colors"
                />
                <button
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#667386] hover:text-[#9AA6B5] transition-colors"
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="mb-4 rounded-lg bg-[#7F1D1D]/20 border border-[#7F1D1D]/40 px-3 py-2.5 text-[12px] text-[#FCA5A5]">
              {error}
            </div>
          )}

          <button
            onClick={isSignup ? handleSignup : handleLogin}
            disabled={loading}
            className="w-full h-11 bg-[#8B5CF6] hover:bg-[#7C3AED] disabled:opacity-60 disabled:cursor-not-allowed text-white text-[14px] font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-[#8B5CF6]/20 hover:shadow-[#8B5CF6]/30 mb-4"
          >
            {loading ? <Loader2 size={15} className="animate-spin" /> : <ArrowRight size={15} />}
            {loading ? (isSignup ? "Creating account…" : "Signing in…") : isSignup ? "Create account" : "Sign in"}
          </button>

          <button
            onClick={swapMode}
            className="w-full text-center text-[12.5px] text-[#667386] hover:text-[#8B5CF6] transition-colors mb-4"
          >
            {isSignup ? "Already have an account? Sign in" : "New to the workbench? Create an account"}
          </button>

          {/* Security note */}
          <div className="rounded-lg bg-[#141E2F] border border-[#253248] p-3 flex items-start gap-2.5">
            <Lock size={12} className="text-[#14B8A6] flex-none mt-0.5" />
            <p className="text-[11px] text-[#9AA6B5] leading-relaxed">
              Your authentication occurs locally within ApexPetro's infrastructure. Credentials are not transmitted externally.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
