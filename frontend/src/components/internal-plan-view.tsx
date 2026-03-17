"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Network, Database, Brain, UserCircle, ActivitySquare } from "lucide-react";

export function InternalPlanView({ activeAgentId = "orchestrator" }: { activeAgentId?: string }) {
  const baseAgents = [
    { id: "orchestrator", name: "Orchestrator", type: "Gateway", status: "Idle", icon: Network, color: "text-indigo-400", bg: "bg-indigo-400/10" },
    { id: "rag", name: "RAG Agent", type: "Pinecone / Vector", status: "Idle", icon: Database, color: "text-emerald-400", bg: "bg-emerald-400/10" },
    { id: "tutor", name: "Socratic Tutor", type: "Pedagogy", status: "Idle", icon: Brain, color: "text-purple-400", bg: "bg-purple-400/10" },
    { id: "profile", name: "Profile Manager", type: "Firestore", status: "Idle", icon: UserCircle, color: "text-amber-400", bg: "bg-amber-400/10" },
    { id: "assessor", name: "Silent Assessor", type: "Evaluation", status: "Idle", icon: ActivitySquare, color: "text-cyan-400", bg: "bg-cyan-400/10" },
  ];

  const activeAgents = baseAgents.map(a => ({
      ...a,
      status: a.id === activeAgentId || (a.id === "orchestrator" && !activeAgentId) ? "Active" : "Idle"
  }));

  return (
    <Card className="border-slate-800 bg-slate-950/50 backdrop-blur w-full shadow-2xl h-full">
      <CardHeader className="pb-3 border-b border-slate-800">
        <CardTitle className="text-sm font-medium tracking-tight text-slate-300 flex items-center justify-between">
          <span>A2A Diagnostic Network</span>
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="p-0">
        <ScrollArea className="h-[250px] w-full p-4">
          <div className="space-y-4">
            <div className="text-xs text-slate-500 font-mono mb-2 uppercase tracking-wide">
              MCP Registry: Local Node Connected
            </div>
            
            <div className="grid gap-3">
              {activeAgents.map((agent) => (
                <div key={agent.id} className={`flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 ${agent.status === "Active" ? "border-emerald-500/50 bg-emerald-950/20 shadow-[0_0_15px_rgba(16,185,129,0.15)] scale-[1.02]" : "border-slate-800 bg-slate-900/50 backdrop-blur"}`}>
                  <div className={`p-2 rounded-md ${agent.bg}`}>
                    <agent.icon className={`h-4 w-4 ${agent.color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-200 truncate">{agent.name}</p>
                    <p className="text-xs text-slate-500 truncate">{agent.type}</p>
                  </div>
                  <div className="text-right flex items-center gap-2">
                    {agent.status === "Active" && (
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                    )}
                    <div className={`text-xs font-mono font-medium ${agent.status === "Active" ? "text-emerald-400" : "text-slate-500"}`}>{agent.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
