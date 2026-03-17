"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles, Trophy, BookOpen, Send } from "lucide-react";

export function OnboardingScreen({ onComplete }: { onComplete: (profile: any) => void }) {
  const [experience, setExperience] = useState("beginner");
  const [goals, setGoals] = useState("");
  const [topics, setTopics] = useState("");
  const [selectedCerts, setSelectedCerts] = useState<string[]>([]);
  const [tags, setTags] = useState("");
  const [knowledge, setKnowledge] = useState("");
  const [useDeepSearch, setUseDeepSearch] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const availableCerts = [
    "AWS Certified", "Azure Solutions Architect", "Google Cloud Professional", 
    "HashiCorp Terraform", "CKA/CKAD", "Snowflake Core", "Databricks Engineer",
    "OCI Architect", "CompTIA Security+", "CISSP", "PMP"
  ];

  const toggleCert = (cert: string) => {
    setSelectedCerts(prev => 
      prev.includes(cert) ? prev.filter(c => c !== cert) : [...prev, cert]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    setTimeout(() => {
        onComplete({
            experience_level: experience,
            goals: goals,
            primary_topics: topics,
            certifications: selectedCerts.join(", "),
            tags: tags,
            knowledge: knowledge,
            use_deep_search: useDeepSearch
        });
        setIsLoading(false);
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-blue-600 via-indigo-500 to-white px-4 overflow-y-auto py-10">
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-40">
        <div className="absolute top-0 right-0 w-[50%] h-[50%] bg-white/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-0 w-[50%] h-[50%] bg-blue-400/20 rounded-full blur-[120px]" />
      </div>

      <Card className="w-full max-w-xl border-white/20 bg-white/90 backdrop-blur-xl shadow-2xl relative z-10 border-t-white/30 my-auto">
        <CardHeader className="text-center space-y-1 pb-2">
          <div className="mx-auto w-14 h-14 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mb-4 shadow-xl shadow-blue-600/20">
            <Sparkles className="text-white w-8 h-8" />
          </div>
          <CardTitle className="text-3xl font-black tracking-tight text-slate-900">
            Personalize Your Engine
          </CardTitle>
          <CardDescription className="text-slate-500 font-medium">
            Configure Aion's Multi-Agent Fleet for your specific mission
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6 pt-4">
          <form onSubmit={handleSubmit} className="space-y-5">
            
            {/* 1. ULTIMATE GOAL (TOP) */}
            <div className="space-y-2">
                <label className="text-[11px] uppercase font-black text-blue-600 ml-1 tracking-widest flex items-center gap-2">
                    <Sparkles className="w-3 h-3" /> Ultimate Learning Goal
                </label>
                <div className="relative group">
                    <Input 
                    placeholder="e.g. Architect a production-grade RAG pipeline from scratch" 
                    className="bg-white border-slate-200 text-slate-900 h-14 pl-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-lg font-semibold shadow-sm"
                    value={goals}
                    onChange={(e) => setGoals(e.target.value)}
                    required
                    />
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-[10px] uppercase font-bold text-slate-400 ml-1 tracking-wider">Experience Level</label>
                    <div className="relative">
                        <select 
                            value={experience} 
                            onChange={(e) => setExperience(e.target.value)}
                            className="w-full bg-white border border-slate-200 text-slate-900 h-11 px-3 rounded-md focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none appearance-none font-medium shadow-sm"
                        >
                            <option value="beginner">Beginner (No background)</option>
                            <option value="intermediate">Intermediate (Some knowledge)</option>
                            <option value="advanced">Advanced (Industry pro)</option>
                            <option value="expert">Architect / Research Level</option>
                        </select>
                        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                            <BookOpen className="w-4 h-4" />
                        </div>
                    </div>
                </div>
                <div className="space-y-2">
                    <label className="text-[10px] uppercase font-bold text-slate-400 ml-1 tracking-wider">Primary Topics</label>
                    <div className="relative group">
                        <Input 
                        placeholder="e.g. Distributed Systems, AI" 
                        className="bg-white border-slate-200 text-slate-900 h-11 px-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm font-medium"
                        value={topics}
                        onChange={(e) => setTopics(e.target.value)}
                        />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                    <label className="text-[10px] uppercase font-bold text-slate-400 ml-1 tracking-wider">User Identity Tags</label>
                    <div className="relative group">
                        <Input 
                        placeholder="Developer, Student, Researcher" 
                        className="bg-white border-slate-200 text-slate-900 h-11 px-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm font-medium"
                        value={tags}
                        onChange={(e) => setTags(e.target.value)}
                        />
                    </div>
                </div>
                <div className="space-y-2">
                    <label className="text-[10px] uppercase font-bold text-slate-400 ml-1 tracking-wider">Deep Search Mode</label>
                    <div className="flex items-center h-11 px-4 bg-white border border-slate-200 rounded-md shadow-sm">
                        <label className="flex items-center gap-3 cursor-pointer text-sm font-medium text-slate-600">
                            <input 
                                type="checkbox" 
                                className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500/20" 
                                checked={useDeepSearch}
                                onChange={(e) => setUseDeepSearch(e.target.checked)}
                            />
                            Perplexity Sonar Research
                        </label>
                    </div>
                </div>
            </div>

            <div className="space-y-2">
                <label className="text-[10px] uppercase font-bold text-slate-400 ml-1 tracking-wider">Current Knowledge Base</label>
                <textarea 
                    placeholder="Briefly describe your existing technical background..." 
                    className="w-full bg-white border border-slate-200 text-slate-900 h-24 p-3 rounded-md focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all outline-none resize-none text-sm font-medium shadow-sm"
                    value={knowledge}
                    onChange={(e) => setKnowledge(e.target.value)}
                />
            </div>

            <div className="space-y-3">
                <label className="text-[10px] uppercase font-bold text-slate-400 ml-1 tracking-wider">Active Certifications & Credentials</label>
                <div className="flex flex-wrap gap-2">
                    {availableCerts.map(cert => (
                        <div 
                            key={cert}
                            onClick={() => toggleCert(cert)}
                            className={`px-3 py-1.5 border rounded-full text-xs font-bold cursor-pointer transition-all flex items-center gap-1.5 shadow-sm ${
                                selectedCerts.includes(cert) 
                                ? 'bg-blue-600 border-blue-600 text-white shadow-blue-500/30' 
                                : 'bg-white border-slate-200 text-slate-600 hover:border-blue-400 hover:bg-blue-50'
                            }`}
                        >
                            <Trophy className={`w-3 h-3 ${selectedCerts.includes(cert) ? 'text-white' : 'text-slate-400'}`} />
                            {cert}
                        </div>
                    ))}
                </div>
            </div>

            <Button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white h-14 font-black text-lg shadow-xl shadow-blue-600/20 mt-4 rounded-xl transition-all active:scale-[0.98]" disabled={isLoading}>
              {isLoading ? "Synchronizing Agent Fleet..." : "Launch Learning Engine"}
              <Send className="ml-2 h-5 w-5" />
            </Button>
            
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
