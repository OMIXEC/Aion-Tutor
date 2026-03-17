"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useAppStore } from "@/lib/store";

interface ProgressDashboardProps {
  userId?: string;
  profile?: any;
}

export function ProgressDashboard({ userId, profile: initialProfile }: ProgressDashboardProps) {
  const storeProfile = useAppStore(state => state.profile);
  const storeProgress = useAppStore(state => state.progress);
  const storeMastery = useAppStore(state => state.masteryTopics);

  const profile = storeProfile || initialProfile;
  const bgCtx = profile?.background_context || profile || {};
  const topicMastery: Record<string, number> = Object.keys(storeMastery).length > 0 ? storeMastery : (profile?.topic_mastery || {});
  
  // Build skills from topic_mastery (live Supabase data) or fall back to topic list from onboarding
  const topics: string[] = (bgCtx.primary_topics || bgCtx.mission)
    ? (bgCtx.primary_topics || bgCtx.mission).split(",").map((t: string) => t.trim()).filter(Boolean)
    : [];
  
  const skills = Object.keys(topicMastery).length > 0
    ? Object.entries(topicMastery).map(([name, progress]) => ({ name, progress: progress as number }))
    : topics.map((t) => ({ name: t, progress: 0 }));

  const overallProgress = storeProgress > 0 ? storeProgress : (skills.length > 0 
    ? Math.round(skills.reduce((acc, s) => acc + s.progress, 0) / skills.length) 
    : 0);

  const goalLabel = profile?.learning_goal || "Learning in Progress";
  const certLabel = bgCtx.certifications || "—";
  const expLevel = bgCtx.experience_level || "beginner";

  return (
    <Card className="border-slate-800 bg-slate-950/50 backdrop-blur w-full shadow-2xl">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-medium tracking-tight text-white">Student Mastery</CardTitle>
          <Badge className="bg-indigo-600/20 text-indigo-400 border-indigo-700 hover:bg-indigo-600/30 capitalize">{expLevel}</Badge>
        </div>
        <p className="text-sm text-slate-400 truncate" title={goalLabel}>{goalLabel}</p>
        {certLabel !== "—" && (
          <p className="text-xs text-emerald-400 mt-1">🏆 {certLabel}</p>
        )}
      </CardHeader>
      
      <CardContent className="space-y-6">
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-slate-300 font-medium">Overall Progress</span>
            <span className="text-indigo-400 font-medium">{overallProgress}%</span>
          </div>
          <Progress value={overallProgress} className="h-2.5 bg-slate-800">
            <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full" style={{ width: `${overallProgress}%` }} />
          </Progress>
        </div>

        {skills.length > 0 ? (
          <div className="space-y-4 pt-2">
            <h4 className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-3">Topic Mastery</h4>
            {skills.map((skill) => (
              <div key={skill.name} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-200">{skill.name}</span>
                  <span className="text-xs font-mono text-slate-400">{skill.progress}%</span>
                </div>
                <div className="flex items-center gap-3">
                  <Progress value={skill.progress} className="h-1.5 flex-1 bg-slate-800">
                    <div 
                      className={`h-full rounded-full transition-all ${
                        skill.progress > 70 ? "bg-emerald-500" : skill.progress > 40 ? "bg-indigo-500" : "bg-rose-500"
                      }`}
                      style={{ width: `${skill.progress}%` }} 
                    />
                  </Progress>
                  <span className="text-xs text-slate-500 w-8 text-right">{skill.progress}%</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500 text-center py-4">Start learning to track topic mastery here.</p>
        )}
      </CardContent>
    </Card>
  );
}

