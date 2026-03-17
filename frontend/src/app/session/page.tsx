"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ChatInterface } from "@/components/chat-interface";
import { ProgressDashboard } from "@/components/progress-dashboard";
import { InternalPlanView } from "@/components/internal-plan-view";
import { useAppStore } from "@/lib/store";
import { supabase } from "@/lib/supabase";

export default function SessionPage() {
  const router = useRouter();
  const profile = useAppStore((state) => state.profile);
  const sessionId = useAppStore((state) => state.session_id);
  const setSessionId = useAppStore((state) => state.setSessionId);
  
  const [activeAgentId, setActiveAgentId] = useState<string>("orchestrator");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        router.push("/");
        return;
      }
      if (!profile) {
        // Fallback: If no profile in store, let's just go back to root which handles checking
        router.push("/");
        return;
      }

      if (!sessionId) {
        // Optional: call a backend `/api/session/new` here instead of random string
        setSessionId(`session_${Math.random().toString(36).substring(7)}`);
      }
      setLoading(false);
    };
    checkAuth();
  }, [router, profile, sessionId, setSessionId]);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    useAppStore.setState({ profile: null, session_id: null });
    router.push("/");
  };

  if (loading || !profile || !sessionId) {
    return <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-500">Initializing Core Agents...</div>;
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 relative overflow-hidden selection:bg-indigo-500/30">
      
      {/* Background ambient gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/20 rounded-full blur-[120px] mix-blend-screen pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-600/10 rounded-full blur-[120px] mix-blend-screen pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 h-screen flex flex-col">
        <header className="flex justify-between items-center mb-8 relative z-10">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white mb-1 bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">
              Aion Cognitive Tutor
            </h1>
            <p className="text-slate-400 text-sm">A2A Multi-Agent Architecture powered by ADK &amp; MCP</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
               <p className="text-[10px] text-slate-500 uppercase font-black">Local User</p>
            </div>
            <div
              className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-full text-xs font-medium text-emerald-400 shadow-lg shadow-emerald-500/5 cursor-pointer hover:bg-slate-800 transition-colors"
              onClick={handleSignOut}
            >
              System Online • Reset
            </div>
          </div>
        </header>

        <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-12 gap-8 relative z-10">
          {/* Left Column: Chat */}
          <div className="lg:col-span-8 flex flex-col min-h-0 h-full">
            <ChatInterface 
              profile={{ background_context: profile, learning_goal: profile.goal }} 
              userId={"local_user"}
              sessionId={sessionId}
              onAgentChange={(agentStr) => setActiveAgentId(agentStr.toLowerCase())} 
            />
          </div>

          {/* Right Column: Dashboards */}
          <div className="lg:col-span-4 flex flex-col gap-8 min-h-0 h-full overflow-y-auto pr-2 pb-8">
            <ProgressDashboard profile={{ background_context: profile, learning_goal: profile.goal }} />
            <InternalPlanView activeAgentId={activeAgentId} />
          </div>
        </div>
      </div>
    </main>
  );
}
