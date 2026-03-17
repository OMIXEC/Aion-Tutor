"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { Button } from "@/components/ui/button";
import { useAppStore } from "@/lib/store";

export default function Home() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        checkProfile(session.user.id);
      } else {
        setLoading(false);
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        checkProfile(session.user.id);
      } else {
        setLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, [router]);

  const checkProfile = async (userId: string) => {
    // Check if user has a profile in Supabase
    const { data, error } = await supabase
      .from("profiles")
      .select("*")
      .eq("id", userId)
      .single();

    if (data) {
      useAppStore.getState().setProfile(data);
      router.push("/session");
    } else {
      router.push("/onboarding");
    }
  };

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");

  const handleAuth = async (isSignUp: boolean) => {
    setAuthError("");
    if (isSignUp) {
      const { error } = await supabase.auth.signUp({ email, password });
      if (error) setAuthError(error.message);
      else setAuthError("Check your email for the confirmation link.");
    } else {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) setAuthError(error.message);
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-500">Initializing Cognitive Engine...</div>;
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-white p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400">
            Aion Tutor
          </h1>
          <p className="text-slate-400 mt-2">Your personalized multi-agent learning engine.</p>
        </div>
        
        <div className="flex flex-col gap-4 mt-8 bg-slate-900/50 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
          {authError && <p className="text-rose-400 text-sm text-center bg-rose-500/10 p-2 rounded-lg">{authError}</p>}
          <div className="space-y-4">
            <div>
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Email</label>
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                placeholder="astronout@aion.dev"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Password</label>
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full mt-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
                placeholder="••••••••"
              />
            </div>
          </div>
          <div className="flex gap-3 mt-4">
            <Button onClick={() => handleAuth(false)} className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/20">
              Sign In
            </Button>
            <Button onClick={() => handleAuth(true)} variant="outline" className="flex-1 border-slate-700 hover:bg-slate-800 text-slate-300">
              Sign Up
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

